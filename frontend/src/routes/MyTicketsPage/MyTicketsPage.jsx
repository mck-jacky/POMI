/* eslint-disable react-hooks/exhaustive-deps */
import React, { useContext, useEffect, useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import NavBar from '../../components/NavBar'
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';
import Ticket2 from '../../components/MyTicket/MyTicket';
import FormControlLabel from '@mui/material/FormControlLabel';
import FilterListIcon from '@mui/icons-material/FilterList';
import { UserContext } from '../../userContext';
import { fetchURL } from '../../helper';
import Alert from '@mui/material/Alert';
import CheckIcon from '@mui/icons-material/Check';
import Avatar from '@mui/material/Avatar';
import { Radio, RadioGroup } from '@mui/material';

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

const MyTicketsPage = () => {
  const userObj = useContext(UserContext);

  const [email, setEmail] = useState("")
  const [ticketList, setTicketsList] = useState([])
  const [show, setShow] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [errorMessage, setErrorMessage] = useState('Error')
  const [filterOption, setFilterOption] = useState('upcoming')

  const handleFilterChange = (event) => {
    setFilterOption(event.target.value);
  };

  const handleSuccess = () => {
    setShowSuccess(true)
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const handleError = (message) => {
    setErrorMessage(message)
    setShow(true)
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const handleFetchEventList = async () => {

    let API = '';
    if (filterOption === "upcoming") {
      API = "user/events/booked"
    } else if (filterOption === "past") {
      API = 'user/events/booked/past'
    }

    const requestData = {
      input_email: userObj.user.email
    };

    const res = await fetchURL(API, 'POST', requestData);

    console.log(res)
    if (res.code === 400) {
      console.log(res)
    } else {
      // setEventList(res);
      let lst = []
      for (const event of res) {
        let exist = false

        for (const item of lst) {
          if (event.event_id === item.id) {
            item.tickets.push({ticketId: event.ticket_code, ticketSeat: event.seat_number})
            exist = true
            break
          }
        }

        if (exist === false) {
          lst.push({
            id: event.event_id,
            title: event.event_title,
            time: event.event_details.start_date_time,
            location: event.event_details.venue,
            tickets: [{ticketId: event.ticket_code, ticketSeat: event.seat_number}]
          })
        }
      }

      console.log(lst)
      setTicketsList(lst)

    }

  };

  useEffect(() => {
    setEmail(userObj.user.email)
    handleFetchEventList();
  }, [filterOption])

  return (
    <ThemeProvider theme={theme}>
      <React.Fragment>
        <NavBar />

        {showSuccess &&
          <Alert icon={<CheckIcon fontSize="inherit" />} severity="success">
            Cancelled Successfully.
          </Alert>
        }
        {show &&
          <Alert severity='error' onClose={() => setShow(false)}>{errorMessage}</Alert>
        }

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            position: 'relative'
          }}
        >
          <Box
            sx={{
              width: 1080,
              display: 'flex',
              paddingTop: 5,
            }}>
            
            {/* LEFT */}
            <Box
              sx={{
                // backgroundColor: 'red',
                width: '25%',
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
                Tickets
              </Typography>

              {ticketList.map((ticket) => (
                <Ticket2 
                  id={ticket.id}
                  name={ticket.title}
                  time={ticket.time}
                  location={ticket.location}
                  tickets={ticket.tickets}
                  handleSuccess={handleSuccess}
                  handleError={handleError}
                />
              ))}

            </Box>

          </Box>


        </Box>

      </React.Fragment>
    </ThemeProvider>
  )
}

export default MyTicketsPage