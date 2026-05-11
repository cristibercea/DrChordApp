import { useState } from 'react';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import {AppBar, Box, Toolbar, IconButton, Typography, Menu, Avatar, Button, MenuItem, Divider, Container} from '@mui/material';


export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const [anchorElUser, setAnchorElUser] = useState(null); // Stare pentru meniul MUI
  const handleOpenUserMenu = (event) => {setAnchorElUser(event.currentTarget)};
  const handleCloseUserMenu = () => {setAnchorElUser(null)};
  const handleLogout = () => {handleCloseUserMenu(); logout(); navigate('/login')};
  const isHome = location.pathname === '/';

  return (
    <AppBar
      position="sticky"
      color="inherit"
      elevation={0}
      sx={{ borderBottom: 1, borderColor: 'grey.200', zIndex: (theme) => theme.zIndex.drawer + 1 }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between', minHeight: '64px' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {/* Logo */}
            <Box component={RouterLink} to="/" sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none', color: 'inherit' }}>
              <Avatar variant="rounded" sx={{ bgcolor: 'primary.main', width: 32, height: 32, mr: 1, fontWeight: 'bold' }}>
                DC
              </Avatar>
              <Typography noWrap
                variant="h6"
                sx={{
                  display: { xs: 'none', sm: 'flex' },
                  fontWeight: 700,
                  letterSpacing: '-.05rem',
                  color: 'text.primary',
                }}
              >DrChord</Typography>
            </Box>

            {/* Links */}
            <Box sx={{ display: { xs: 'none', sm: 'flex' }, height: '64px' }}>
              <Button disableRipple component={RouterLink} to="/"
                sx={{
                  color: isHome ? 'primary.main' : 'text.secondary',
                  display: 'flex',
                  alignItems: 'center',
                  fontWeight: isHome ? 600 : 500,
                  borderRadius: 0,
                  borderBottom: isHome ? '2px solid' : '2px solid transparent',
                  borderColor: isHome ? 'primary.main' : 'transparent',
                  '&:hover': {backgroundColor: 'transparent', color: 'primary.main'}
                }}
              > My songs </Button>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ display: { xs: 'none', sm: 'block' } }}>
              Welcome, <Box component="span" fontWeight="600" color="text.primary">{user?.name || 'User'}</Box>
            </Typography>

            {/* Avatar Button */}
            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
              <Avatar sx={{ width: 36, height: 36, bgcolor: 'grey.100', color: 'text.primary', fontSize: '0.875rem', fontWeight: 'bold' }}>
                {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </Avatar>
            </IconButton>

            {/* Dropdown Menu */}
            <Menu keepMounted
              sx={{ mt: '45px' }}
              id="menu-appbar"
              anchorEl={anchorElUser}
              anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
              open={Boolean(anchorElUser)}
              onClose={handleCloseUserMenu}
              PaperProps={{elevation: 3, sx: { minWidth: 200, mt: 1, borderRadius: 2 }}}
            >
              <Box sx={{ px: 2, py: 1.5, display: { xs: 'block', sm: 'none' } }}>
                <Typography variant="body2" fontWeight="bold" color="text.primary" noWrap> {user?.name} </Typography>
                <Typography variant="caption" color="text.secondary" noWrap> {user?.email} </Typography>
              </Box>
              <Divider sx={{ display: { xs: 'block', sm: 'none' }, mb: 1 }} />
              <MenuItem component={RouterLink} to="/profile" onClick={handleCloseUserMenu} sx={{ py: 1.5 }}>
                <Typography textAlign="center" variant="body2">Account Settings</Typography>
              </MenuItem>
              <MenuItem onClick={handleLogout} sx={{ py: 1.5 }}>
                <Typography textAlign="center" variant="body2" color="error.main">Log out</Typography>
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}