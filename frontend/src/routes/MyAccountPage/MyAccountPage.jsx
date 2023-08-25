/* eslint-disable react-hooks/exhaustive-deps */
import React, { useContext, useEffect, useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import NavBar from '../../components/NavBar';
import { Box, Paper } from '@mui/material';
import Typography from '@mui/material/Typography';
import MyAccountBox from '../../components/MyAccountBox';
import SearchIcon from '@mui/icons-material/Search';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SettingsIcon from '@mui/icons-material/Settings';
import PaymentsIcon from '@mui/icons-material/Payments';
import { UserContext } from '../../userContext';
import { Link } from 'react-router-dom';
import './MyAccountPage.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#99c5c4',
    },
    secondary: {
      main: '#00FF00',
    },
  },
});

const MyAccountPage = () => {
  const userObj = useContext(UserContext);

  const [email, setEmail] = useState("")

  useEffect(() => {
    setEmail(userObj.user.email)
  }, [])

  return (
    <ThemeProvider theme={theme}>
      <NavBar />
    
      <div className="ocean">
        <div className="wave"></div>
        <div className="wave"></div>
      </div>
      
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          position: 'relative',
          zIndex: 999,
        }}
      >
        <Box
          sx={{
            width: 1080,
            paddingTop: 6,
            position: 'relative',
            zIndex: 1,
            overflow: 'hidden',
          }}
        >

          <Typography
            sx={{
              fontSize: "32px",
              fontWeight: 600,
              color: "rgb(34, 34, 34)",
              lineHeight: "0px"
            }}
          >
            Account
          </Typography>
          <Typography
            sx={{
              fontSize: "18px",
              fontWeight: 400,
              color: "rgb(34, 34, 34)",
              lineHeight: "70px"
            }}
          >
            {email}
          </Typography>
          <div className="MyAccountPage2">
          <Paper elevation={0} className="wave-container" sx={{ borderRadius: '20px' }}>
          <Box
            sx={{
              marginTop: 4,
              display: 'flex',
              flexWrap: 'wrap',
              zindex: 1
            }}
          >

            <Link to="/search_history">
              <MyAccountBox>
                <SearchIcon
                  sx={{
                    width: "32px",
                    height: "32px",
                    color: "#222222",
                    zindex: 1
                  }}
                />
                <Typography
                  sx={{
                    marginTop: 5,
                    marginBottom: 1,
                    fontSize: "16px",
                    lineHeight: "20px",
                    color: "#222222",
                    fontWeight: 600
                  }}
                >
                  Search history
                </Typography>
                <Typography
                  sx={{
                    fontSize: "14px",
                    lineHeight: "18px",
                    color: "#717171",
                    fontWeight: 400 
                  }}
                >
                  Review your past searches with the search history feature
                </Typography>
                
              </MyAccountBox>
            </Link>
            
            <Link to="/reset_password">
              <MyAccountBox>
                <RestartAltIcon
                  sx={{
                    width: "32px",
                    height: "32px",
                    color: "#222222"
                  }}
                />
                <Typography
                  sx={{
                    marginTop: 5,
                    marginBottom: 1,
                    fontSize: "16px",
                    lineHeight: "20px",
                    color: "#222222",
                    fontWeight: 600 
                  }}
                >
                  Reset Password
                </Typography>
                <Typography
                  sx={{
                    fontSize: "14px",
                    lineHeight: "18px",
                    color: "#717171",
                    fontWeight: 400 
                  }}
                >
                  Update your password and secure your account
                </Typography>
                
              </MyAccountBox>
            </Link>

            <MyAccountBox>
              <PaymentsIcon
                sx={{
                  width: "32px",
                  height: "32px"
                }}
              />
              <Typography
                sx={{
                  marginTop: 5,
                  marginBottom: 1,
                  fontSize: "16px",
                  lineHeight: "20px",
                  color: "#222222",
                  fontWeight: 600 
                }}
              >
                Payment details
              </Typography>
              <Typography
                sx={{
                  fontSize: "14px",
                  lineHeight: "18px",
                  color: "#717171",
                  fontWeight: 400 
                }}
              >
                Review your saved payment details for quick and secure transactions
              </Typography>
              
            </MyAccountBox>

            <MyAccountBox>
              <SettingsIcon
                sx={{
                  width: "32px",
                  height: "32px"
                }}
              />
              <Typography
                sx={{
                  marginTop: 5,
                  marginBottom: 1,
                  fontSize: "16px",
                  lineHeight: "20px",
                  color: "#222222",
                  fontWeight: 600 
                }}
              >
                Setting
              </Typography>
              <Typography
                sx={{
                  fontSize: "14px",
                  lineHeight: "18px",
                  color: "#717171",
                  fontWeight: 400 
                }}
              >
                Set your default language, currency, and timezone
              </Typography>
              
            </MyAccountBox>
            <Link to="/account_insights">
              <MyAccountBox>
                <AnalyticsIcon
                  sx={{
                    width: "32px",
                    height: "32px"
                  }}
                />
                <Typography
                  sx={{
                    marginTop: 5,
                    marginBottom: 1,
                    fontSize: "16px",
                    lineHeight: "20px",
                    color: "#222222",
                    fontWeight: 600 
                  }}
                >
                  Account Insights
                </Typography>
                <Typography
                  sx={{
                    fontSize: "14px",
                    lineHeight: "18px",
                    color: "#717171",
                    fontWeight: 400 
                  }}
                >
                  Get insights on your account acitivty
                </Typography>
                
              </MyAccountBox>
            </Link>

          </Box>
          </Paper>
          </div>
        </Box>
      </Box>
      

    </ThemeProvider>
  )
}

export default MyAccountPage