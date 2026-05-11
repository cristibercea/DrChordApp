import { useState, useEffect } from 'react';
import api from '../api/jwtInterceptor';
import {Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, Alert, Box, Typography, IconButton} from '@mui/material';

export default function EditSongModal({ isOpen, onClose, song, onEditSuccess }) {
  const [name, setName] = useState('');
  const [genre, setGenre] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {if (song) {setName(song.name || ''); setGenre(song.genre || '')}}, [song]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await api.put(`/songs/${song.id}`, {name: name, genre: genre,});
      onEditSuccess();
      onClose();
    } catch (err) {setError(err.response?.data?.detail || 'Failed to update song details. Please try again.')
    } finally {setIsLoading(false)}
  };
  if (!song) return null;

  return (
    <Dialog open={isOpen} onClose={onClose} fullWidth maxWidth="xs" PaperProps={{sx: { borderRadius: 2 }}}>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pb: 1 }}>
        <Typography variant="h6" fontWeight="bold">Edit Song Details</Typography>
        <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
          <span style={{ fontSize: '1.5rem', lineHeight: 1 }}>&times;</span>
        </IconButton>
      </DialogTitle>

      <Box component="form" onSubmit={handleSubmit}>
        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 3 }}>
          {error && (<Alert severity="error">{error}</Alert>)}
          <TextField fullWidth required
            label="Song Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., My Awesome Riff"
          />
          <TextField fullWidth required
            label="Genre / Tags"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="e.g., Acoustic, Rock, Blues"
          />
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={onClose} disabled={isLoading} color="inherit" sx={{ fontWeight: 'medium' }}> Cancel </Button>
          <Button disableElevation
            type="submit"
            disabled={isLoading}
            variant="contained"
            color="primary"
            sx={{ fontWeight: 'bold' }}
          > {isLoading ? 'Saving...' : 'Save Changes'} </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}