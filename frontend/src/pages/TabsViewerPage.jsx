import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/jwtInterceptor';
import {Container, Box, Typography, Button, CircularProgress, Alert, Paper} from '@mui/material';


export default function TabsViewerPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [song, setSong] = useState(null);
  const [tabContent, setTabContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTabAndSongDetails = async () => {
      setIsLoading(true);
      try {
        const response = await api.get(`/songs/${id}/tab`);
        setSong(response.data.song);
        setTabContent(response.data.tab_content);
        // eslint-disable-next-line no-unused-vars
      } catch (_) {setError('Failed to load the tablature. It might have been deleted or is currently unavailable.')
      } finally {setIsLoading(false)}
    };

    fetchTabAndSongDetails();
  }, [id]);

  const handleDownload = async (file_format) => {
    try {
      const response = await api.get(`/songs/${id}/download?file_format=${file_format}`, {responseType: 'blob',});
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      const fileName = song?.name ? `${song.name.replace(/\s+/g, '_')}.${file_format}` : `tablature.${file_format}`;
      link.setAttribute('download', fileName);

      document.body.appendChild(link);
      link.click();

      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      // eslint-disable-next-line no-unused-vars
    } catch (err) {alert(`Failed to download the ${file_format.toUpperCase()} file. Please try again.`)}
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 64px)' }}>
        <CircularProgress size={60} thickness={4} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 8 }}>
        <Alert
          severity="error"
          variant="outlined"
          sx={{ py: 3, px: 4, borderRadius: 2, alignItems: 'center', display: 'flex', flexDirection: 'column', gap: 2 }}
        >
          <Typography variant="h6" color="error.main" textAlign="center"> {error} </Typography>
          <Button
            variant="contained"
            color="error"
            onClick={() => navigate('/')}
            disableElevation
            sx={{ mt: 2, fontWeight: 'bold' }}
          > Back to Dashboard </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Top Navigation & Header */}
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { md: 'center' }, gap: 3, mb: 4 }}>
        <Box>
          <Button
            onClick={() => navigate('/')}
            color="inherit"
            sx={{ mb: 1, color: 'primary', textTransform: 'none', fontWeight: 'medium', '&:hover': { color: 'primary.main', bgcolor: 'transparent' } }}
          > &larr; Back to My Songs </Button>
          <Typography variant="h4" component="h1" fontWeight="bold" color="text.primary" gutterBottom> {song?.name || 'Unknown Song'} </Typography>
          <Typography variant="body1" color="text.primary">Genre: {song?.genre || 'N/A'} </Typography>
        </Box>

        {/* Download Options (CF7) */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mr: 1, width: { xs: '100%', sm: 'auto' } }}>
            Download as:
          </Typography>
          {['txt', 'pdf', 'docx', 'odt', 'midi'].map((format) => (
            <Button
              key={format}
              onClick={() => handleDownload(format)}
              variant="outlined"
              size="small"
              sx={{
                textTransform: 'uppercase',
                fontWeight: 'bold',
                color: 'primary',
                borderColor: 'grey.300',
                '&:hover': {
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  bgcolor: 'primary.50'
                }
              }}
            > .{format} </Button>
          ))}
        </Box>
      </Box>

      {/* Tablature Viewer Area (CF6) */}
      <Paper
        elevation={4}
        sx={{
          bgcolor: '#0f172a', // slate-900
          color: '#f8fafc', // slate-50
          borderRadius: 3,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: '#1e293b' // slate-800
        }}
      >
        <Box sx={{ bgcolor: '#1e293b', px: 3, py: 1.5, borderBottom: '1px solid', borderColor: '#334155' }}>
          <Typography variant="caption" sx={{ fontFamily: 'monospace', textTransform: 'uppercase', letterSpacing: 1, color: '#94a3b8' }}>
            Tabs for {song?.name || 'Unknown Song'}
          </Typography>
        </Box>

        <Box sx={{ p: { xs: 3, sm: 4 }, overflowX: 'auto' }}>
          <Typography
            component="pre"
            sx={{
              fontFamily: 'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
              fontSize: '0.875rem',
              lineHeight: 1.6,
              m: 0,
              whiteSpace: 'pre',
              fontWeight: 500
            }}
          > {tabContent || 'No tabs available for this song.'} </Typography>
        </Box>
      </Paper>
    </Container>
  );
}