import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../api/jwtInterceptor';
import { useAuthStore } from '../store/authStore';
import UploadSongModal from "../components/UploadSongModal";
import SongCard from '../components/SongCard';
import FilterBar from '../components/FilterBar';
import EditSongModal from '../components/EditSongModal';
import {Container, Box, Typography, Button, Grid, CircularProgress, Alert, Paper} from '@mui/material';


export default function Dashboard() {
  const [songs, setSongs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const token = useAuthStore((state) => state.token);
  const ws = useRef(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [songToEdit, setSongToEdit] = useState(null);
  const [page, setPage] = useState(1);
  const limit = 10;
  const [filters, setFilters] = useState({search: '', genre: '', hasTab: 'all', sortBy: 'date_desc'});

  const handleOpenEdit = (song) => {setSongToEdit(song); setIsEditModalOpen(true)};
  const fetchSongs = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const offset = (page - 1) * limit;
      const params = new URLSearchParams({
        limit: limit,
        offset: offset,
        ...(filters.search && { search: filters.search }),
        ...(filters.genre && { genre: filters.genre }),
        hasTab: filters.hasTab,   // 'all', 'yes', 'no'
        sortBy: filters.sortBy    // 'date_desc', 'name_asc', etc.
      });

      const response = await api.get(`/songs?${params.toString()}`);
      setSongs(response.data.items || []);

    } catch (err) {setError('Song list failed to load.'); console.error(err)
    } finally {setIsLoading(false)}
  }, [page, filters, limit]);

  useEffect(() => {
    if (!token) return;
    ws.current = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    ws.current.onopen = () => { console.log('WebSocket Connected') };
    ws.current.onclose = () => { console.log('WebSocket Disconnected') };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'TAB_READY') { // tab ready events are registered using WebSockets
        setSongs((prevSongs) =>
          prevSongs.map((song) =>
            song.id === data.song_id ? { ...song, has_tabs: true, isGenerating: false } : song
          )
        );
        alert(`Success: Tab for song "${data.song_name}" is ready!`);
      } else if (data.event === 'TAB_FAILED') {
        setSongs((prevSongs) =>
          prevSongs.map((song) =>
            song.id === data.song_id ? { ...song, isGenerating: false } : song
          )
        );
        alert(`Error: ${data.error}`);
      }
    };
    return () => {if (ws.current) ws.current.close();};
  }, [token]);

  useEffect(() => {fetchSongs()}, [fetchSongs]);

  // Funcția pentru ștergere (CF4.3)
  const handleDeleteSong = async (songId) => {
    if (!window.confirm('Are you sure? Tabs and MIDI will be lost!')) return;
    try {
      await api.delete(`/songs/${songId}`);
      setSongs(songs.filter(song => song.id !== songId));
      // eslint-disable-next-line no-unused-vars
    } catch (err) {alert('Error deleting song.')}
  };

  // Tabs Generation (CF5)
  const handleGenerateTab = async (songId) => {
    try {
      setSongs((prevSongs) =>
        prevSongs.map((song) =>
          song.id === songId ? { ...song, isGenerating: true } : song
        )
      );
      await api.post(`/songs/${songId}/generate-tab`);
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      alert('Transcription failed to start.');
      setSongs((prevSongs) =>
        prevSongs.map((song) =>
          song.id === songId ? { ...song, isGenerating: false } : song
        )
      );
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Modals */}
      <UploadSongModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onUploadSuccess={fetchSongs}/>
      <EditSongModal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} song={songToEdit} onEditSuccess={fetchSongs}/>

      {/* Page Header */}
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { sm: 'center' }, mb: 4, gap: 2 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold" color="text.primary"> My songs </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}> Manage and transcribe songs </Typography>
        </Box>
        <Button disableElevation variant="contained" color="primary" onClick={() => setIsModalOpen(true)} sx={{ fontWeight: 'bold' }}>
          Upload recording
        </Button>
      </Box>

      {/* Filter bar */}
      <Paper elevation={0} sx={{ mb: 4, p: 2, border: '1px solid', borderColor: 'grey.200', borderRadius: 3 }}>
        <FilterBar filters={filters} setFilters={setFilters} />
      </Paper>

      {error && (<Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>)}

      {isLoading ? (<Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>) : (
        <>
          {/* SongCard Grid */}
          {songs.length > 0 ? (
            <Grid container spacing={3}>
              {songs.map((song) => (
                <Grid item xs={12} sm={6} md={4} key={song.id}>
                  <SongCard song={song} onDelete={handleDeleteSong} onGenerateTab={handleGenerateTab} onEdit={handleOpenEdit}/>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper variant="outlined"
              sx={{ py: 10, textAlign: 'center', borderStyle: 'dashed', borderRadius: 3, borderColor: 'grey.300', bgcolor: 'grey.50' }}
            >
              <Typography variant="h6" color="text.secondary"> No recordings </Typography>
            </Paper>
          )}

          {/* Paging */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 6 }}>
            <Button
              variant="outlined"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              sx={{ fontWeight: 'medium' }}
            > Back </Button>
            <Typography variant="body2" color="text.secondary" fontWeight="medium"> Page {page} </Typography>
            <Button
              variant="outlined"
              onClick={() => setPage(p => p + 1)}
              disabled={songs.length < limit}
              sx={{ fontWeight: 'medium' }}
            > Next </Button>
          </Box>
        </>
      )}
    </Container>
  );
}