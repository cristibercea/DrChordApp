import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import api from '../api/jwtInterceptor';
import {Container, Box, Typography, TextField, Button, Alert, Link, Paper, Avatar} from '@mui/material';


export default function RegisterPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) { setError('Passwords do not match!'); return}
    setError('');
    setIsLoading(true);
    try {
      await api.post('/auth/request-signup', {name: name, email: email, password: password,}); //store temp new user data
      navigate('/verify-code', { state: { email: email } });
    } catch (err) {setError(err.response?.data?.detail || "Error when creating account.");
    } finally {setIsLoading(false)}
  };

  return (
    <Container component="main" maxWidth="xs"
      sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}
    >
      <Paper elevation={3} sx={{ p: 4, width: '100%', borderRadius: 3 }}>
        {/* Form Header */}
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
          <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 48, height: 48, fontWeight: 'bold' }}> DC </Avatar>
          <Typography component="h1" variant="h4" fontWeight="bold" color="secondary"> DrChord </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}> Create a new account </Typography>
        </Box>

        {error && (<Alert severity="error" sx={{ mb: 3 }}> {error} </Alert>)}

        {/* Form */}
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          <TextField required fullWidth autoFocus
            label="Full Name"
            name="name"
            autoComplete="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="John Doe"
          />

          <TextField required fullWidth
            label="Email Address"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@example.com"
          />

          <TextField required fullWidth
            name="password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder=""
          />

          <TextField required fullWidth
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder=""
          />

          <Button fullWidth disableElevation
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 1, py: 1.5, fontWeight: 'bold' }}
          > {isLoading ? 'Creating account...' : 'Sign Up'} </Button>

          {/* Link to Login */}
          <Box sx={{ textAlign: 'center', mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Link
                component={RouterLink}
                to="/login"
                variant="body2"
                fontWeight="bold"
                underline="hover"
                color="primary"
              > Sign in </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}