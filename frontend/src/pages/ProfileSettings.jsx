import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import api from '../api/jwtInterceptor';
import {Container, Typography, Box, Paper, TextField, Button, Alert, Divider, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions} from '@mui/material';


export default function ProfileSettings() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const login = useAuthStore((state) => state.login);
  const logout = useAuthStore((state) => state.logout);
  const token = useAuthStore((state) => state.token);
  const [name, setName] = useState(user?.name || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);

  // CF1.2: Account update
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await api.put('/users/me', {
        name: name,
        current_password: currentPassword,
        new_password: newPassword ? newPassword : null,
      });
      login({ ...user, name: response.data.name }, token);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setCurrentPassword('');
      setNewPassword('');
    } catch (err) {setMessage({type: 'error', text: err.response?.data?.detail || 'Failed to update profile.'})
    } finally {setIsLoading(false)}
  };

  // CF1.3: Account delete
  const handleConfirmDelete = async () => {
    setOpenDeleteDialog(false);
    try {
      await api.delete('/users/me');
      logout();
      navigate('/register');
      // eslint-disable-next-line no-unused-vars
    } catch (err) {setMessage({type: 'error', text: 'Failed to delete account. Please try again later.'})}
  };

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      {/* Page header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold" color="text.primary"> Account Settings </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}> Update your personal information or delete your account. </Typography>
      </Box>

      {message.text && (<Alert severity={message.type} sx={{ mb: 4 }}> {message.text} </Alert>)}

      {/* Edit Account (CF1.2) */}
      <Paper variant="outlined" sx={{ mb: 6, borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ px: 3, py: 2, bgcolor: 'grey.50', borderBottom: 1, borderColor: 'grey.200' }}>
          <Typography variant="h6" fontWeight="medium" color="text.primary"> Profile Information </Typography>
        </Box>

        <Box component="form" onSubmit={handleUpdateProfile} sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
          <TextField disabled fullWidth
            label="Email Address"
            type="email"
            value={user?.email || ''}
            helperText="Email cannot be changed."
          />

          <TextField fullWidth required
            label="Full Name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle1" fontWeight="medium" color="text.primary"> Change Password (Optional) </Typography>

          <TextField fullWidth
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Leave blank to keep current password"

          />
          <TextField fullWidth
            label="Current Password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Enter current password to save changes"
          />

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
            <Button type="submit" variant="contained" color="primary" disabled={isLoading || !currentPassword} sx={{ px: 4 }} disableElevation>
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Delete Account (CF1.3) */}
      <Paper variant="outlined" sx={{borderColor: 'error.main', bgcolor: 'error.50', borderRadius: 2, overflow: 'hidden'}}>
        <Box sx={{ px: 3, py: 2, bgcolor: 'error.100', borderBottom: 1, borderColor: 'error.main' }}>
          <Typography variant="h6" fontWeight="medium" color="error.dark"> Danger Zone </Typography>
        </Box>
        <Box sx={{ p: 3 }}>
          <Typography variant="body2" color="error.dark" sx={{ mb: 2 }}>
            Once you delete your account, there is no going back. Please be certain.
          </Typography>
          <Button variant="contained" color="error" onClick={() => setOpenDeleteDialog(true)} disableElevation> Delete Account </Button>
        </Box>
      </Paper>

      {/* Confirmation Dialogue */}
      <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title" color="error"> {"Delete Account?"} </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure that you want to delete your account? All your uploaded songs and generated tablatures will be permanently lost. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenDeleteDialog(false)} color="inherit"> Cancel </Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained" autoFocus disableElevation> Yes, Delete </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}