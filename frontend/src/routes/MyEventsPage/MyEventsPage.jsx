/* eslint-disable react-hooks/exhaustive-deps */
import React, { useContext, useEffect, useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import NavBar from '../../components/NavBar'
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';
import FilterListIcon from '@mui/icons-material/FilterList';
import { UserContext } from '../../userContext';
import { fetchURL } from '../../helper';
import Avatar from '@mui/material/Avatar';
import EventCard from '../../components/EventCard/EventCard';
import CircularProgress from '@mui/material/CircularProgress';
import { Radio, RadioGroup, FormControlLabel } from '@mui/material';
import { useLocation } from 'react-router-dom';

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

const MyEventsPage = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const param = queryParams.get('email')

  const userObj = useContext(UserContext);

  const [email, setEmail] = useState("")
  const [fetchIsReady, setFetchIsReady] = useState(false);
  const [eventList, setEventList] = useState([]);
  const [filterOption, setFilterOption] = useState('upcoming')

  const handleFilterChange = (event) => {
    setFilterOption(event.target.value);
  };

  const handleFetchEventList = async () => {
    setFetchIsReady(false)

    let API = '';
    if (filterOption === "upcoming") {
      API = "user/events/created"
    } else if (filterOption === "past") {
      API = 'user/events/created/past'
    }

    const requestData = {
      input_email: param !== null ? param : userObj.user.email
    };

    const res = await fetchURL(API, 'POST', requestData);
    
    console.log(res);
    if (res.code === 400) {
      console.log(res);
    } else {
      setEventList(res);
    }

    setFetchIsReady(true);
  };

  useEffect(() => {
    if (param) {
      setEmail(param)
    } else {
      setEmail(userObj.user.email)
    }
    handleFetchEventList();
  }, [filterOption, location.pathname])

  return (
    <ThemeProvider theme={theme}>
      <React.Fragment>
        <NavBar />

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            position: 'relative'
          }}
        >
          <Box
            sx={{
              width: 1480,
              display: 'flex',
              paddingTop: 5,
            }}>
            
            {/* LEFT */}
            <Box
              sx={{
                // backgroundColor: 'red',
                width: '25%',
                paddingLeft: 20
              }} 
            >
              <Avatar sx={{ bgcolor: 'black' }} >{email[0]}</Avatar>
              <Typography
                sx={{
                  fontSize: "18px",
                  fontWeight: 700,
                  color: "rgb(34, 34, 34)",
                  lineHeight: "70px"
                }}
              >
                {email}
              </Typography>

              <Typography
                sx={{
                  fontSize: "18px",
                  fontWeight: 700,
                  color: "rgb(34, 34, 34)",
                  lineHeight: "60px"
                }}
              >
                <FilterListIcon 
                  sx={{
                    marginRight: 1,
                    marginTop: '-5px'
                  }}
                />
                Filters
              </Typography>
              
              <RadioGroup 
                value={filterOption} 
                onChange={handleFilterChange}
              >
                <FormControlLabel 
                  value="upcoming" 
                  control={<Radio />} 
                  label="Upcoming" 
                />
                <FormControlLabel 
                  value="past" 
                  control={<Radio />} 
                  label="Past" 
                />
              </RadioGroup>

            </Box>

            {/* RIGHT */}
            <Box
              sx={{
                width: '75%'
              }}
            >
              <Typography
                sx={{
                  fontSize: "18px",
                  fontWeight: 700,
                  color: "rgb(34, 34, 34)",
                  lineHeight: "70px"
                }}
              >
                Events
              </Typography>

              <Box
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
              }}
              >
              {fetchIsReady ? (
                eventList.length > 0 ? (
                  eventList.map((event) => (
                    <EventCard
                      title={event.event_title}
                      start_date_time={event.event_details.start_date_time}
                      venue={event.event_details.venue}
                      image={event.image}
                      type={event.event_type}
                      id={event.event_id}
                    />
                  ))
                ) : (
                  <Typography
                    sx={{
                      display: 'flex',
                      justifyContent: 'center',
                      marginTop: 5,
                      marginBottom: 5
                    }}
                  >
                    No events found. Start hosting to create an event
                  </Typography>
                )
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    marginTop: 5
                  }}
                >
                  <CircularProgress color="primary" />
                </Box>
              )}
              </Box>

            </Box>

          </Box>


        </Box>

      </React.Fragment>
    </ThemeProvider>
  )
}

export default MyEventsPage