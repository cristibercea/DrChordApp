import { useState } from 'react';
import api from '../api/jwtInterceptor';
import {Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, Alert, Box, Typography, IconButton} from '@mui/material';


export default function UploadSongModal({ isOpen, onClose, onUploadSuccess }) {
  const [name, setName] = useState('');
  const [genre, setGenre] = useState('');
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!file) {setError('Please select an audio file.'); return}
    setIsLoading(true);

    const formData = new FormData();
    formData.append('name', name);
    formData.append('genre', genre);
    formData.append('file', file);

    try {
      await api.post('/songs', formData, {headers: {'Content-Type': 'multipart/form-data',},});
      setName('');
      setGenre('');
      setFile(null);
      onUploadSuccess();
      onClose();
    } catch (err) {setError(err.response?.data?.detail || 'Failed to upload the song. Please try again.')
    } finally {setIsLoading(false)}
  };

  return (
    <Dialog open={isOpen} onClose={onClose} fullWidth maxWidth="xs" PaperProps={{sx: { borderRadius: 2 }}}>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pb: 1 }}>
        <Typography variant="h6" fontWeight="bold"> Add New Recording </Typography>
        <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
          <span style={{ fontSize: '1.5rem', lineHeight: 1 }}>&times;</span>
        </IconButton>
      </DialogTitle>

      <Box component="form" onSubmit={handleSubmit}>
        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 3 }}>
          {error && (<Alert severity="error"> {error} </Alert>)}

          <TextField
            label="Song Name"
            fullWidth
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., My Awesome Riff"
          />

          <TextField
            label="Genre / Tags"
            fullWidth
            required
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="e.g., Acoustic, Rock, Blues"
          />

          {/* Upload file section */}
          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 'medium' }}> Audio/MIDI File * </Typography>
            <Button fullWidth
              variant="outlined"
              component="label"

              sx={{
                justifyContent: 'flex-start',
                textTransform: 'none',
                color: file ? 'text.primary' : 'text.secondary',
                borderColor: 'grey.400',
                py: 1.5,
                '&:hover': {borderColor: 'primary.main', bgcolor: 'primary.50'}
              }}
            >
              {file ? file.name : 'Choose a file...'}
              <input hidden required type="file" accept=".mp3,.wav,.ogg,.flac"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </Button>
          </Box>
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={onClose} disabled={isLoading} color="inherit" sx={{ fontWeight: 'medium' }}> Cancel </Button>
          <Button disableElevation
            type="submit"
            disabled={isLoading}
            variant="contained"
            color="primary"
            sx={{ fontWeight: 'bold' }}
          > {isLoading ? 'Uploading...' : 'Upload Song'} </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}