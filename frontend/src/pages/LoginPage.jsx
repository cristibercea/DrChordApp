import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../api/jwtInterceptor';
import {Container, Box, Typography, TextField, Button, Alert, Link, Paper, Avatar} from '@mui/material';


export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const response = await api.post('/auth/login', {email: email, password: password,});
      const { token, user } = response.data;
      login(user, token);
      navigate('/');
    } catch (err) {setError(err.response?.data?.detail || 'Authentication error. Check credentials.')
    } finally {setIsLoading(false)}
  };

  return (
    <Container component="main" maxWidth="xs"
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <Paper elevation={3} sx={{ p: 4, width: '100%', borderRadius: 3 }}>
        {/* Form header */}
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
          <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 48, height: 48, fontWeight: 'bold' }}> DC </Avatar>
          <Typography component="h1" variant="h4" fontWeight="bold" color="secondary"> DrChord </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}> Log in to continue </Typography>
        </Box>

        {error && (<Alert severity="error" sx={{ mb: 3 }}> {error} </Alert>)}

        {/* Form */}
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          <TextField required fullWidth autoFocus
            id="email"
            label="Email Address"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <TextField required fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button fullWidth disableElevation
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 1, py: 1.5, fontWeight: 'bold' }}
          > {isLoading ? 'Loading...' : 'Log in'} </Button>

          {/* Link to Sign up */}
          <Box sx={{ textAlign: 'center', mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Don&#39;t have an account?{' '}
              <Link component={RouterLink} to="/register" variant="body2" fontWeight="bold" underline="hover" color="primary"> Sign up! </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}