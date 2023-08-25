import React, { useContext } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Badge from '@mui/material/Badge';
import MenuItem from '@mui/material/MenuItem';
import Menu from '@mui/material/Menu';
import AddIcon from '@mui/icons-material/Add';
import AccountCircle from '@mui/icons-material/AccountCircle';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber';
import MoreIcon from '@mui/icons-material/MoreVert';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Link, useNavigate } from 'react-router-dom';
import { UserContext } from '../../userContext';
import { isLogin } from '../../helper';
import SearchFunction from '../../routes/SearchFunction';
import { fetchURL } from '../../helper';
import PersonIcon from '@mui/icons-material/Person';
import EventIcon from '@mui/icons-material/Event';
import LogoutIcon from '@mui/icons-material/Logout';

const theme = createTheme({
  palette: {
    primary: {
      main: '#99c5c4', // Replace with your desired primary color
    },
    secondary: {
      main: '#00FF00', // Replace with your desired secondary color
    },
  },
});

const NavBar = () => {
  const userObj = useContext(UserContext);
  const navigate = useNavigate();

  const [anchorEl, setAnchorEl] = React.useState(null);
  const [mobileMoreAnchorEl, setMobileMoreAnchorEl] = React.useState(null);

  const isMenuOpen = Boolean(anchorEl);
  const isMobileMenuOpen = Boolean(mobileMoreAnchorEl);

  async function logout (event) {
    event.preventDefault();

    const res = await fetchURL('auth/logout', 'POST', {
      token: userObj.user.token
    });
    
    console.log(res)

    if (res.code === 400) {
      console.log(res.message)
    } else {

    }

    setAnchorEl(null);
    handleMobileMenuClose();

    userObj.setUser({});
    localStorage.removeItem('token');
    localStorage.removeItem('email');

    navigate('/');
  }

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMoreAnchorEl(null);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    handleMobileMenuClose();
  };

  const handleMyEvents = () => {
    handleMenuClose();

    navigate('/my_events');
  }

  const handleMobileMenuOpen = (event) => {
    setMobileMoreAnchorEl(event.currentTarget);
  };

  const menuId = 'primary-search-account-menu';
  const renderMenu = (
    <Menu
      anchorEl={anchorEl}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      id={menuId}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isMenuOpen}
      onClose={handleMenuClose}
    >
      <Link to="/my_account" onClick={handleMenuClose} style={{ textDecoration: 'none', color: 'inherit' }}>
        <MenuItem>
        <PersonIcon
          sx={{
            marginRight: 1
          }}
        />
          My account
        </MenuItem>
      </Link>
      <Link to="/event_create" style={{ color: 'inherit', textDecoration: 'inherit' }}></Link>
      <MenuItem onClick={handleMyEvents}>
        <EventIcon
          sx={{
            marginRight: 1
          }}
        />
        My events
      </MenuItem>
      <MenuItem onClick={logout}>
        <LogoutIcon
          sx={{
            marginRight: 1
          }}
        />
        Log out
      </MenuItem>
    </Menu>
  );

  const mobileMenuId = 'primary-search-account-menu-mobile';
  const renderMobileMenu = (
    <Menu
      anchorEl={mobileMoreAnchorEl}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      id={mobileMenuId}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isMobileMenuOpen}
      onClose={handleMobileMenuClose}
    >
      <MenuItem>
        <IconButton size="large" aria-label="create an event" color="inherit">
          <Badge>
            <AddIcon />
          </Badge>
        </IconButton>
        <p>Create an event</p>
      </MenuItem>
      <MenuItem>
        <IconButton size="large" aria-label="tickets" color="inherit">
          <Badge>
            <ConfirmationNumberIcon />
          </Badge>
        </IconButton>
        <p>Tickets</p>
      </MenuItem>
      <MenuItem onClick={handleProfileMenuOpen}>
        <IconButton
          size="large"
          aria-label="account of current user"
          aria-controls="primary-search-account-menu"
          aria-haspopup="true"
          color="inherit"
        >
          <AccountCircle />
        </IconButton>
        <p>Profile</p>
      </MenuItem>
    </Menu>
  );

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color='primary'>
          <Toolbar>

            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', sm: 'block' } }}
            >
              <Link to="/" style={{ color: 'inherit', textDecoration: 'inherit' }}>
                POMI
              </Link>
            </Typography>

            <Box sx={{ flexGrow: 1 }} />

            <SearchFunction />

            <Box sx={{ flexGrow: 1 }} />
            
            {isLogin(userObj)
              ? <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
                  <IconButton size="large" aria-label="create an event" color="inherit">
                    <Badge>
                      <Link to="/event_create" style={{ color: 'inherit', textDecoration: 'inherit' }}>
                        <AddIcon />
                      </Link>
                    </Badge>
                  </IconButton>
                  <IconButton size="large" aria-label="tickets" color="inherit">
                    <Badge>
                      <Link to="/my_tickets" style={{ color: 'inherit', textDecoration: 'inherit' }}>
                        <ConfirmationNumberIcon />
                      </Link>
                    </Badge>
                  </IconButton>
                  <IconButton
                    size="large"
                    edge="end"
                    aria-label="account of current user"
                    aria-controls={menuId}
                    aria-haspopup="true"
                    onClick={handleProfileMenuOpen}
                    color="inherit"
                  >
                    <AccountCircle />
                  </IconButton>
                </Box>
              :
                <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
                  <Typography
                    variant="h6"
                    component="div"
                    sx={{ display: { xs: 'none', sm: 'block' }, marginRight: 2 }}
                  >
                    <Link to="/login" style={{ color: 'inherit', textDecoration: 'inherit' }}>
                      Login
                    </Link>
                  </Typography>

                  <Typography
                    variant="h6"
                    component="div"
                    sx={{ display: { xs: 'none', sm: 'block' } }}
                  >
                    <Link to="/register" style={{ color: 'inherit', textDecoration: 'inherit' }}>
                      Register
                    </Link>
                  </Typography>
                </Box>
            }
            
            <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
              <IconButton
                size="large"
                aria-label="show more"
                aria-controls={mobileMenuId}
                aria-haspopup="true"
                onClick={handleMobileMenuOpen}
                color="inherit"
              >
                <MoreIcon />
              </IconButton>
            </Box>
            
          </Toolbar>
        </AppBar>
        {renderMobileMenu}
        {renderMenu}
      </Box>
    </ThemeProvider>
  );
}

export default NavBar