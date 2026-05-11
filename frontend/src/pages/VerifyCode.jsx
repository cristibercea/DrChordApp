import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api/jwtInterceptor';
import {Container, Typography, TextField, Button, Box, Alert, Paper } from '@mui/material';

export default function VerifyCode() {
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState(location.state?.email || '');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await api.post('/auth/verify-and-register', { email, code });
      alert('Account verification successful!');
      navigate('/login');
    } catch (err) { setError(err.response?.data?.detail || 'Invalid verification code. Please try again.')
    } finally { setIsLoading(false)}
  };

  return (
    <Container maxWidth="xs" sx={{ mt: 10 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Box component="form" onSubmit={handleVerify} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box textAlign="center">
            <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom> Verify Email </Typography>
            <Typography variant="body2" color="text.secondary"> A 6 digit verification code was sent to your email address. </Typography>
          </Box>

          {error && <Alert severity="error">{error}</Alert>}

          <TextField
            label="Email address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            fullWidth
            disabled={!!location.state?.email}
          />

          <TextField
            label="6 digit verification code"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))} // Permite doar numere
            required
            fullWidth
            inputProps={{
              maxLength: 6,
              style: { textAlign: 'center', letterSpacing: '0.75rem', fontSize: '1.5rem', fontWeight: 'bold' }
            }}
          />

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading || code.length !== 6 || !email}
            fullWidth
            disableElevation
            sx={{ py: 1.5, fontWeight: 'bold' }}
          > {isLoading ? 'Processing...' : 'Verify account'} </Button>
        </Box>
      </Paper>
    </Container>
  );
}