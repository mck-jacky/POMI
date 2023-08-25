import React, { useContext, useEffect, useState } from 'react';
import { fetchURL } from '../../helper';
import { UserContext } from '../../userContext';
import NavBar from '../../components/NavBar';
import { Box, Paper } from '@mui/material';
import { Link } from 'react-router-dom';
import Typography from '@mui/material/Typography';

const AcctInsightsPage = () => {
  const userObj = useContext(UserContext);

  const [email, setEmail] = useState("")

  const [userAnalytics, setUserAnalytics] = useState(null);

  const fetchUserAnalytics = async () => {
    console.log('here')
    try {
      const res = await fetchURL('user/analytics', 'POST', {
        token: localStorage.token, // Pass the user's token as a parameter
      });
      setUserAnalytics(res); // Store the response data in state
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchUserAnalytics();
    setEmail(userObj.user.email)
  }, []);

  return (
    <div>
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
            // overflow: 'hidden',
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
            Insights
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
            {/* jacky@gmail.com */}
          </Typography>

          <Box
            sx={{
              marginTop: 4,
              display: 'flex',
              flexWrap: 'wrap',
              zindex: 1
            }}
          >

            <Box
              sx={{
                backgroundColor: '#d3ebeb',
                boxShadow: "0px 6px 16px rgba(0, 0, 0, 0.12)",
                minHeight: "220px",
                padding: "16px",
                borderRadius: "12px",
                marginRight: "13px",
                marginBottom: "13px",
                width: "340px",
                maxHeight: "168px",
                height: "168px",
                display: "flex",
                color: 'black',
                textAlign: "center",
                justifyContent: "center",
              }}
              >
                <Box>
                <Typography
                    sx={{
                        marginBottom: 3,
                        fontSize: "23px",
                        textAlign: "center",
                    }}
                  >
                    Event Participation
                  </Typography>

                  <Typography
                    sx={{
                        fontSize: "60px",
                        fontWeight: "bold",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        textAlign: "center",
                    }}
                    >
                    {userAnalytics?.num_events_participated}
                  </Typography>
                </Box>
            </Box>

            <Box
              sx={{
                backgroundColor: '#d3ebeb',
                boxShadow: "0px 6px 16px rgba(0, 0, 0, 0.12)",
                minHeight: "220px",
                padding: "16px",
                borderRadius: "12px",
                marginRight: "13px",
                marginBottom: "13px",
                width: "340px",
                maxHeight: "168px",
                height: "168px",
                color: 'black'
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  height: '100%',
                }}
              >
                  <Typography
                    sx={{
                      marginBottom: 3,
                      fontSize: "23px",
                      textAlign: "center",
                    }}
                  >
                    Favourite Event Type
                  </Typography>

                  <Typography
                    sx={{
                      fontSize: "60px",
                      fontWeight: "bold",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      textAlign: "center",
                    }}
                  >
                    {userAnalytics?.favourite_event_type}
                  </Typography>
                </Box>
            </Box>

            <Box
              sx={{
                backgroundColor: '#d3ebeb',
                boxShadow: "0px 6px 16px rgba(0, 0, 0, 0.12)",
                minHeight: "220px",
                padding: "16px",
                borderRadius: "12px",
                marginRight: "13px",
                marginBottom: "13px",
                width: "340px",
                maxHeight: "168px",
                height: "168px",
                color: 'black'
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  height: '100%',
                }}
              >
                  <Typography
                    sx={{
                      marginBottom: 3,
                      fontSize: "23px",
                      textAlign: "center",
                    }}
                  >
                    Favourite Host
                  </Typography>

                  <Typography
                    sx={{
                      fontSize: "60px",
                      fontWeight: "bold",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      textAlign: "center",
                    }}
                  >
                    {userAnalytics?.favourite_host}
                  </Typography>
                </Box>
            </Box>

          </Box>
        </Box>
      </Box>
    </div>
  );
};

export default AcctInsightsPage;