/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useContext } from 'react';
import NavBar from '../../components/NavBar'
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import image1 from '../../images/landing1.jpg'
import image2 from '../../images/landing2.jpg'
import image3 from '../../images/landing3.jpg'
import image4 from '../../images/landing4.jpg'
import image5 from '../../images/landing5.jpg'
import EventCard from '../../components/EventCard';
import { fetchURL } from '../../helper';
import { UserContext } from '../../userContext';
import CircularProgress from '@mui/material/CircularProgress';

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

const LandingPage2 = () => {
  const [fetchIsReady, setFetchIsReady] = useState(false);
  const [eventList, setEventList] = useState([]);
  const [forYouEventList, setForYouEventList] = useState([]);
  const userObj = useContext(UserContext);

  const settings = {
    dots: true,
    infinite: true,
    slidesToShow: 2,
    slidesToScroll: 1,
    autoplay: true, // Enable autoplay
    autoplaySpeed: 3000, // Set autoplay speed in milliseconds
  };

  const handleFetchEventList = async () => {
    try {
      const res = await fetchURL("event/list/get", "GET");
      setEventList(res);
    } catch (error) {
      console.error(error);
    }

    setFetchIsReady(true)
  };

  const handleFetchPersonalizedEventList = async () => {
    const res = await fetchURL('event/recommendations', 'POST', {
      email: userObj.user.email,
    })
    console.log(res)
    if (res.code === 400) {
      console.error(res.message);
    } else {
      setForYouEventList(res);
    }
  };

  useEffect(() => {
    handleFetchEventList();
    handleFetchPersonalizedEventList();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <NavBar />
        <Box
          sx={{
            display: "flex",
            justifyContent: "center"
          }}
        >
          {/* Main Container */}
          <Box
            sx={{
              width: "1480px",
            }}
          >
            <Typography
              sx={{
                fontSize: "27px",
                fontWeight: 700,
                color: "rgb(34, 34, 34)",
                letterSpacing: ".05em",
                marginTop: 2,
              }}
            >
              FEATURES
            </Typography>

            <Slider {...settings}>
              <Box
                component="img"
                sx={{
                  objectFit: "cover",
                  maxHeight: "322px",
                  maxWidth: "723px",
                  borderRadius: "10px",
                }}
                alt="event-image"
                src={image1}
              />
              <Box
                component="img"
                sx={{
                  objectFit: "cover",
                  maxHeight: "322px",
                  maxWidth: "723px",
                  borderRadius: "10px"
                }}
                alt="event-image"
                src={image2}
              />
              <Box
                component="img"
                sx={{
                  objectFit: "cover",
                  maxHeight: "322px",
                  maxWidth: "723px",
                  borderRadius: "10px"
                }}
                alt="event-image"
                src={image3}
              />
              <Box
                component="img"
                sx={{
                  objectFit: "cover",
                  maxHeight: "322px",
                  maxWidth: "723px",
                  borderRadius: "10px"
                }}
                alt="event-image"
                src={image4}
              />
              <Box
                component="img"
                sx={{
                  objectFit: "cover",
                  maxHeight: "322px",
                  maxWidth: "723px",
                  borderRadius: "10px"
                }}
                alt="event-image"
                src={image5}
              />
            </Slider>

            <Typography
            sx={{
              fontSize: "27px",
              fontWeight: 700,
              color: "rgb(34, 34, 34)",
              letterSpacing: ".05em",
              marginTop: 2,
              marginBottom: 1
            }}
            >
              RECOMMNEDED FOR YOU
            </Typography>

            {/* Recommended for you Container */}
            <Box
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
              }}
            >
              {fetchIsReady ? (
                forYouEventList.length > 0 ? (
                  forYouEventList.map((event) => (
                    <EventCard
                      title={event.event_title}
                      host={event.host}
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
                    There are no upcoming events
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

            <Typography
              sx={{
                fontSize: "27px",
                fontWeight: 700,
                color: "rgb(34, 34, 34)",
                letterSpacing: ".05em",
                marginTop: 2,
                marginBottom: 1
              }}
            >
              Upcoming Events
            </Typography>

            {/* Upcoming events Container */}
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
                      host={event.host}
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
                    There are no upcoming events
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
    </ThemeProvider>
  )
}

export default LandingPage2