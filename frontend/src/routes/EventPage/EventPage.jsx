/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useContext } from 'react'
import { Box } from '@mui/system';
import NavBar from '../../components/NavBar'
import Typography from '@mui/material/Typography';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Button from '@mui/material/Button';
import { Carousel } from 'antd';
import AccessTimeOutlinedIcon from '@mui/icons-material/AccessTimeOutlined';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import AddCircleRoundedIcon from '@mui/icons-material/AddCircleRounded';
import RemoveCircleRoundedIcon from '@mui/icons-material/RemoveCircleRounded';
import OutlinedInput from '@mui/material/OutlinedInput';
import Checkbox from '@mui/material/Checkbox';
import ListItemText from '@mui/material/ListItemText';
import { fetchURL } from '../../helper';
import { useNavigate, useParams } from 'react-router-dom';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Alert from '@mui/material/Alert';
import { UserContext } from '../../userContext';
import Backdrop from '@mui/material/Backdrop';
import CircularProgress from '@mui/material/CircularProgress';
import { formatTimeString } from '../../helper';
import ReviewsOutlinedIcon from '@mui/icons-material/ReviewsOutlined';
import Avatar from '@mui/material/Avatar';
import Comment from '../../components/Comment/Comment';
import PermIdentityOutlinedIcon from '@mui/icons-material/PermIdentityOutlined';
import InsightsIcon from '@mui/icons-material/Insights';
import CancelButton from './components/CancelButton/CancelButton';
import BroadcastButton from './components/BroadcastButton';
import { Link } from 'react-router-dom';
import LeaveComment from '../../components/LeaveComment/LeaveComment';

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

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const EventPage = () => {
  const { eventId } = useParams();
  const userObj = useContext(UserContext);

  const [title, setTitle] = useState('')
  const [organiser, setOrganiser] = useState('')
  const [time, setTime] = useState('')
  const [location, setLocation] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [seat, setSeat] = useState([])
  const [image, setImage] = useState('')
  const [category, setCategory] = useState('')
  const [creatorId, setCreatorId] = useState('')
  const [customerComment, setCustomerComment] = useState([])

  const [totalPrice, setTotalPrice] = useState(0)
  const [availableSeats, setAvailableSeats] = useState([])

  const [host, setHost] = useState(false)
  const [show, setShow] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [errorMessage, setErrorMessage] = useState('Error')
  const [successMessage, setSuccessMessage] = useState('Success')

  const [seatNumber, setSeatNumber] = React.useState([]);
  const [processing, setProcessing] = React.useState(false);
  const [nOfTickets, setNOfTickets] = useState(0)

  const [showCommentError, setShowCommentError] = useState(false)
  const [commentErrorMessage, setCommentErrorMessage] = useState('Error')

  const handleDecreaseButton = () => {
    if (nOfTickets === 0) return
    setNOfTickets(nOfTickets - 1)
    console.log(nOfTickets)
    setTotalPrice((nOfTickets-1) * price)

    const sortedList = availableSeats.slice().sort((a, b) => a - b);
    setSeatNumber(sortedList.slice(0, (nOfTickets-1)))
  }

  const handleIncreaseButton = () => {
    if (nOfTickets === availableSeats.length) return
    setNOfTickets(nOfTickets + 1)
    setTotalPrice((nOfTickets + 1) * price)

    const sortedList = availableSeats.slice().sort((a, b) => a - b);
    setSeatNumber(sortedList.slice(0, (nOfTickets+1)))
  }

  const handleSuccess = (message) => {
    setSuccessMessage(message)
    setShowSuccess(true);
  };

  const handleError = (message) => {
    setErrorMessage(message);
    setShow(true);
  };

  const handleCommentError = (message) => {
    setCommentErrorMessage(message)
    setShowCommentError(true)
  }

  const navigate = useNavigate();
  const handleInsightsNavigation = () => {
    navigate(`/event_insights/${eventId}`);
  };

  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    setSeatNumber(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );

    setTotalPrice((seatNumber.length+1) * Number(price))
  };

  const setupControls = (event, comments) => {
    console.log(event)

    setTitle(event.event_title)
    setOrganiser(event.host)
    setTime(formatTimeString(event.event_details.start_date_time))
    setLocation(event.event_details.venue)
    setDescription(event.event_description)
    setPrice(event.ticket_price)
    setSeat(event.seating_plan_image)
    setCategory(event.event_type)
    setAvailableSeats(event.available_seats)
    setCreatorId(event.creator_id)
    setCustomerComment(comments)

    if (event.image === "") {
      setImage('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAC3CAMAAAAGjUrGAAAAM1BMVEXp7vG6vsHs8fS3u77Fycy+wsXc4eTX3N/h5unT2NrHzM7N0tW1ubzu8/W7v8LBxcjl6uwx8f6JAAADy0lEQVR4nO2c23aDIBBFCQheUf//a6vRpEZuJgXj0LNXH7oaK3WXwXEQGAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGnw9Hz7Et+Ds1ElpxoJaeGsHHqRHlkoKlJ0JbvbKQhRjCSs8FKcY+RuRVKQwqsTlUxShm9f8BGGU53cuvryHeXUyLnTj9++5hC8WJ2kv+2sTkR79Y4y9uuf2papKVYnxcWd8GpV0uj0aaxcnFx9lH04ESeMfLpZ2pLJW/obZzrhcGK2BSdmW3BitkXdyfxYz7mO2hZtJ7yqCznIoVUsXv8h7YSPzZJ2CtENZTQplJ1Mj0CbZ6CuiFUdI+yEt69PhUJGih+6Tni5L7qJJlJbZJ2MZu1A1FHuP2Sd7CPnTh+nLapOKtNIrIyOqhNe28puYvjXThp7KfKAE16FDqDqxF6x7sI1VK26wFCcmRMR6gOTEhG6P+XmJNRPtJrruqL0SSHrxD6ehJxwtZS6vVLIOrFP9wTuO1o95XnCh6qTj/ITrsSRQ8k6Ydbg8YYOV9tDhbO4QNaJbUrd301elXikkHUyZbLGc7F34m4bOI9z2ccUuk6Ybl+liMFXP9GGEme/IuxkfubZXKcofL+vVW8ocYUPZSfThRbdYkUIWftKj3YljjyFtBPGtWplL259UzJfZmoLHPeYQtvJMr0zjsxfnnYrsY4p1J0c+l1H4DzOaByfv5N9XhLsKfk7MfOSkJTsnYSVGANt7k50IHBsZ83ciSsv8faUjJxw821w303YLSUfJ7q+VbvPjit5eRs2Gyfzw0//usTkaODsz5yLk6mXTPTbnhLKS5xSMnGyKJnnMn4j4I3AWeie9e8cnGxmSh/h876S55CShZNtEX8Nn3eG1xyd6Nf59FnKsVQtXyf7qR5R6U96SU5OLG9dVB8pyceJbUJQvpOX5OdElx9dfs5OdMxVgnk4ibtwMgsnvI5oJA8nMceSTJxEHUvycBJ/ETZ5JwnWpZN3Yn1n+H874RJODr4LCidwAic74MQETkzgxAROTODEBE5MzDy2i763VEfcCVOlmr+UMr8J/8DxybpIjKyTlG3BidkWnJhtwYnZFpyYbcGJ2VZBwwkb18SqV6lb4usUyeX3NmTrJozzvy81j7S2Sd8l/4a27XeSFHH5jbqfG4OexvVDx7HjSTqu300Y+91p+BS6NuregKnQjn1gEiBCe6RcBl7K6AUCO0VFRMm89EK1RXKatoq4e+QJJN+N+r4jNQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzuIHpk8/wVCHmdcAAAAASUVORK5CYII=')
    } else {
      setImage(event.image)
    }
    if (event.seating_plan_image === "") {
      setSeat('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAC3CAMAAAAGjUrGAAAAM1BMVEXp7vG6vsHs8fS3u77Fycy+wsXc4eTX3N/h5unT2NrHzM7N0tW1ubzu8/W7v8LBxcjl6uwx8f6JAAADy0lEQVR4nO2c23aDIBBFCQheUf//a6vRpEZuJgXj0LNXH7oaK3WXwXEQGAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGnw9Hz7Et+Ds1ElpxoJaeGsHHqRHlkoKlJ0JbvbKQhRjCSs8FKcY+RuRVKQwqsTlUxShm9f8BGGU53cuvryHeXUyLnTj9++5hC8WJ2kv+2sTkR79Y4y9uuf2papKVYnxcWd8GpV0uj0aaxcnFx9lH04ESeMfLpZ2pLJW/obZzrhcGK2BSdmW3BitkXdyfxYz7mO2hZtJ7yqCznIoVUsXv8h7YSPzZJ2CtENZTQplJ1Mj0CbZ6CuiFUdI+yEt69PhUJGih+6Tni5L7qJJlJbZJ2MZu1A1FHuP2Sd7CPnTh+nLapOKtNIrIyOqhNe28puYvjXThp7KfKAE16FDqDqxF6x7sI1VK26wFCcmRMR6gOTEhG6P+XmJNRPtJrruqL0SSHrxD6ehJxwtZS6vVLIOrFP9wTuO1o95XnCh6qTj/ITrsSRQ8k6Ydbg8YYOV9tDhbO4QNaJbUrd301elXikkHUyZbLGc7F34m4bOI9z2ccUuk6Ybl+liMFXP9GGEme/IuxkfubZXKcofL+vVW8ocYUPZSfThRbdYkUIWftKj3YljjyFtBPGtWplL259UzJfZmoLHPeYQtvJMr0zjsxfnnYrsY4p1J0c+l1H4DzOaByfv5N9XhLsKfk7MfOSkJTsnYSVGANt7k50IHBsZ83ciSsv8faUjJxw821w303YLSUfJ7q+VbvPjit5eRs2Gyfzw0//usTkaODsz5yLk6mXTPTbnhLKS5xSMnGyKJnnMn4j4I3AWeie9e8cnGxmSh/h876S55CShZNtEX8Nn3eG1xyd6Nf59FnKsVQtXyf7qR5R6U96SU5OLG9dVB8pyceJbUJQvpOX5OdElx9dfs5OdMxVgnk4ibtwMgsnvI5oJA8nMceSTJxEHUvycBJ/ETZ5JwnWpZN3Yn1n+H874RJODr4LCidwAic74MQETkzgxAROTODEBE5MzDy2i763VEfcCVOlmr+UMr8J/8DxybpIjKyTlG3BidkWnJhtwYnZFpyYbcGJ2VZBwwkb18SqV6lb4usUyeX3NmTrJozzvy81j7S2Sd8l/4a27XeSFHH5jbqfG4OexvVDx7HjSTqu300Y+91p+BS6NuregKnQjn1gEiBCe6RcBl7K6AUCO0VFRMm89EK1RXKatoq4e+QJJN+N+r4jNQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzuIHpk8/wVCHmdcAAAAASUVORK5CYII=')
    } else {
      setSeat(event.seating_plan_image)
    }
    
    if (event.creator_id === userObj.user.email) {
      setHost(true)
    }

  }

  async function fetchEventDetail () {
    const res = await fetchURL('event/searchbyid', 'POST', {
      event_id: eventId
    })

    const comment = await fetchURL('review/read', 'POST', {
      event_id: eventId
    })

    console.log(comment)

    setupControls(res, comment)
    console.log(res)

  }

  React.useEffect(() => {
    fetchEventDetail();
  }, [])

  const [dialogOpen, setDialogOpen] = React.useState(false);

  const handleDialogOpen = () => {
    if (seatNumber.length === 0) {
      setDialogOpen(false)
      setShow(true)
      setShowSuccess(false)
      setErrorMessage("Please select seats or number of tickets")
      setProcessing(false)
      window.scrollTo({ top: 0, behavior: 'smooth' });

      return
    } else {
      setDialogOpen(true);
    }
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };



  async function handleConfirmButton (event) {
    event.preventDefault();

    setProcessing(true)

    const res = await fetchURL('booking/ticket', 'POST', {
      token: userObj.user.token,
      event_id: eventId,
      requested_seats: seatNumber,
      num_tickets_to_purchase: seatNumber.length
    })

    console.log(res)

    if (res.code === 400 || res.code === 500) {
      setDialogOpen(false)
      setShow(true)
      setShowSuccess(false)
      setErrorMessage(res.message.replace(/<\/?p>/g, ''))
      setProcessing(false)
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      handleSuccess("Your ticket purchases was successful. An email confirmation has been sent to your registered address. You will be automatically redirected in 3 seconds...")
      setDialogOpen(false)
      setShow(false)
      setProcessing(false)
      window.scrollTo({ top: 0, behavior: 'smooth' });

      setTimeout(() => {
        navigate('/');
      }, 3000);
    }
    
  }

  async function updateComments () {
    const comment = await fetchURL('review/read', 'POST', {
      event_id: eventId
    })

    setCustomerComment(comment)
  }

  const isTimeBefore = new Date() < new Date(time)

  return (
    <ThemeProvider theme={theme}>
      <React.Fragment>
        <NavBar />

        {showSuccess &&
          <Alert severity='success'>{successMessage}</Alert>
        }
        {show &&
          <Alert severity='error' onClose={() => setShow(false)}>{errorMessage}</Alert>
        }

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginTop: 10
          }}
        >
          <Box sx={{width: 1200}}>
            <Carousel autoplay>
              <Box
                component="img"
                sx={{
                  maxWidth: "1200px",
                  maxHeight: "600px",
                  objectFit: 'cover'
                }}
                alt='event-image'
                src={image}
              />
              <Box
                component="img"
                sx={{
                  maxWidth: "1200px",
                  maxHeight: "600px",
                  objectFit: 'cover'
                }}
                alt='event-seat-map'
                src={seat}
              />
            </Carousel>
          </Box>

          <Box 
            sx={{
              marginTop: 10,
              alignItems: 'flex-start',
              width: 1300,
              paddingLeft: 10,
              display: 'flex'
            }}
          >

            {/* LEFT */}
            <Box
              sx={{
                width: 600,
                marginRight: 10
              }}
            >
              <Typography >
                {/* Music */}
                {category}
              </Typography>
              <Typography 
                sx={{
                  fontWeight: 800,
                  fontSize: 50,
                  lineHeight: 1.1,
                  color: '#1e0a3c',
                  marginBottom: 4
                }}  
              >
                {/* #BeerOps SYDNEY MID2023 - Australia's Largest Tech Networking Event! */}
                {title}
              </Typography>

              {/* Time and Location */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: 4
                }}
              >
                <Typography 
                  sx={{
                    fontSize: 28,
                    color: '#1e0a3c',
                    width: 300
                  }}  
                >
                  <AccessTimeOutlinedIcon
                    sx={{ marginRight: 2 }}
                  />
                  <b>Date and time</b>
                  <Typography>
                    {/* TODO: FORMAT THE TIME */}
                    {time}
                    {/* Tue, 11 Jul 2023 6:00 PM - 9:00 PM AEST */}
                  </Typography>

                </Typography>

                {/* <Box sx={{ margin: 3 }}/> */}

                <Typography 
                  sx={{
                    fontSize: 28,
                    color: '#1e0a3c',
                    width: 300
                  }}  
                >
                  <LocationOnOutlinedIcon
                    sx={{ marginRight: 2 }}
                  />
                  <b>Location</b>
                  <Typography>
                    {/* DOCKSIDE asfas hafs hjkasf hkasfhkasfj kasshfjkas */}
                    {location}
                  </Typography>
                </Typography>

              </Box>

              <Typography 
                sx={{
                  fontSize: 28,
                  color: '#1e0a3c',
                }}  
              >
                <InfoOutlinedIcon
                    sx={{ marginRight: 2 }}
                />
                <b>About this event</b>
              </Typography>

              <Typography 
                sx={{
                  color: '#1e0a3c',
                  marginBottom: 4
                }}  
              >
                {/* Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. */}
                {description}
              </Typography>

              <Typography 
                sx={{
                  fontSize: 28,
                  color: '#1e0a3c',
                  marginBottom: 1
                }}  
              >
                <PermIdentityOutlinedIcon
                    sx={{ marginRight: 2 }}
                />
                <b>About this organiser</b>
              </Typography>

              <Link to={`/users?email=${creatorId}`}>
                <Box
                  sx={{
                    display: 'flex',
                    marginBottom: 4
                  }}
                >
                  <Avatar
                    sx={{
                      height: 50,
                      width: 50,
                      bgcolor: 'black'
                    }}
                  >
                    {organiser[0]}
                  </Avatar>
                  <Typography 
                    sx={{
                      color: '#1e0a3c',
                      marginLeft: 2,
                      alignSelf: 'center',
                      fontSize: 24
                    }}  
                    >
                    {organiser}
                </Typography>
                <Typography 
                    sx={{
                      marginLeft: 2,
                      alignSelf: 'center',
                      fontSize: 15,
                      color: 'grey'                      
                    }}  
                    >
                    id: {creatorId}
                </Typography>
                </Box>
              </Link>
              

              <Typography 
                sx={{
                  fontSize: 28,
                  color: '#1e0a3c',
                  marginBottom: 1
                }}  
              >
                <ReviewsOutlinedIcon
                    sx={{ marginRight: 2 }}
                />
                <b>{customerComment.length} Reviews</b>
              </Typography>

              {showCommentError &&
                <Alert 
                  severity='error'
                  sx={{
                    marginBottom: 2
                  }}
                >
                  {commentErrorMessage}
                </Alert>
              }

              {host === false && userObj.user.token && (
                <LeaveComment 
                  name={userObj.user.email[0]}
                  token={userObj.user.token}
                  eventId={eventId}
                  handleCommentError={handleCommentError}
                  setShowCommentError={setShowCommentError}
                  updateComments={updateComments}
                />
              )}

              {/* COMMENT SECTION */}
              <Box
                sx={{
                  marginBottom: 4
                }}
              >
                {customerComment.length > 0 ? (
                  customerComment.map((comment) => (
                    <Box>
                      <Comment
                        name={comment.customer_name}
                        comment={comment.review_content}
                      />
                      {comment.host_reply && (
                        <Comment
                          host={true}
                          name={comment.host_name}
                          comment={comment.host_reply}
                        />
                      )}
                      {host === true && !comment.host_reply && (
                        <Box
                          sx={{
                            marginLeft: 6
                          }}
                        >
                          <LeaveComment 
                            host={true}
                            name={comment.host_name}
                            hostId={creatorId}
                            eventId={eventId}
                            threadId={comment.thread_id}
                            handleCommentError={handleCommentError}
                            setShowCommentError={setShowCommentError}
                            updateComments={updateComments}
                          />
                        </Box>
                      )}
                    </Box>
                  ))
                ) : (
                  <></>
                )}
                
              </Box>

            </Box>

            {/* RIGHT */}
            {host === false && (

            
              <Box
                sx={{
                  width: 400,
                  display: 'flex',
                  justifyContent: 'flex-end',
                  flexDirection: 'column'
                }}
              >
                <Typography 
                  sx={{
                    fontSize: 28,
                    color: '#1e0a3c',
                    marginBottom: 4
                  }}  
                >
                  <b>Choose Your Tickets</b>
                </Typography>

                {location !== "Online" &&
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between'
                    }}
                  >
                    <Box>

                      <Typography 
                        sx={{
                          color: '#1e0a3c',
                          fontSize: 20
                        }}  
                      >
                        Seat Ticket
                      </Typography>

                      <Typography>
                        {/* $35 */}
                        ${price}
                      </Typography>

                    </Box>

                    <Box
                      sx={{
                        display: 'flex',
                        width: 150,
                        justifyContent: 'space-between',
                      }}
                    >
                      <FormControl sx={{ m: 1, width: 500 }}>
                        <InputLabel id="demo-multiple-checkbox-label">Seat</InputLabel>
                        <Select
                          labelId="demo-multiple-checkbox-label"
                          id="demo-multiple-checkbox"
                          multiple
                          value={seatNumber}
                          onChange={handleChange}
                          input={<OutlinedInput label="Tag" />}
                          renderValue={(selected) => selected.join(', ')}
                          MenuProps={MenuProps}
                          sx={{
                            width: "100%",
                          }}
                        >
                          {availableSeats.map((name) => (
                            <MenuItem key={name} value={name}>
                              <Checkbox checked={seatNumber.indexOf(name) > -1} />
                              <ListItemText primary={name} />
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Box>
                  </Box>
                }

                {location === "Online" &&
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between'
                    }}
                  >
                    <Box>

                      <Typography 
                        sx={{
                          color: '#1e0a3c',
                          fontSize: 20
                        }}  
                      >
                        General Admission
                      </Typography>

                      <Typography>
                        ${price}
                      </Typography>

                    </Box>

                    <Box
                      sx={{
                        display: 'flex',
                        width: 150,
                        justifyContent: 'space-between',
                      }}
                    >
                      <Button onClick={handleDecreaseButton}>
                        <RemoveCircleRoundedIcon 
                          sx={{
                            fontSize: 30
                          }}
                        />
                      </Button>
                      
                      <Typography 
                        sx={{
                          color: '#1e0a3c',
                          fontSize: 25,
                          marginTop: 1
                        }}  
                      >
                        {nOfTickets}
                      </Typography>

                      <Button onClick={handleIncreaseButton}>
                        <AddCircleRoundedIcon 
                          sx={{
                            fontSize: 30
                          }}
                        />
                      </Button>
                    </Box>
                  </Box>
                }

                <Box 
                  sx={{
                    marginTop: 2
                  }}
                />

                <Box
                  sx={{
                    display: 'flex',
                    width: '100%',
                    justifyContent: 'flex-end',
                    marginBottom: 2
                  }}
                >
                    <Typography 
                      sx={{
                        color: '#1e0a3c',
                        fontSize: 25,
                        marginTop: 1
                      }}  
                    >
                      Total: ${totalPrice}
                  </Typography>
                </Box>
                

                <Button 
                  variant="contained" 
                  size="large"
                  sx={{
                    // backgroundColor: '#99c5c4',
                    transition: 'filter 0.3s', // Add transition for a smooth effect
                    '&:hover': {
                      filter: 'brightness(120%)', // Increase brightness on hover
                    }
                  }}
                  onClick={handleDialogOpen}
                >
                  Buy Ticket
                </Button>
                
                {location === "Online" &&
                  <Typography 
                    sx={{
                      color: '#1e0a3c',
                      fontSize: 25,
                      marginTop: 1
                    }}  
                  >
                    tickets left: {availableSeats.length}
                  </Typography>
                }
                
                <Dialog
                  open={dialogOpen}
                  onClose={handleDialogClose}
                  aria-labelledby="alert-dialog-title"
                  aria-describedby="alert-dialog-description"
                >
                  {processing &&
                    <Backdrop
                      sx={{ color: '#fff', zIndex: 999 }}
                      open={true}
                    >
                      <CircularProgress color="inherit" />
                    </Backdrop>
                  }

                  <DialogTitle id="alert-dialog-title">
                    <b>Ticket Purchase Confirmation</b>
                  </DialogTitle>
                  <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                      <Typography
                        sx={{
                          marginBottom: 2
                        }}
                      >
                          You have selected [{seatNumber.length}] seat(s) for the event <b>{title}</b>. Please confirm your purchase.
                        </Typography>
                        {location !== "Online" && 
                          <Typography>Total seats: [{seatNumber.join(', ')}]</Typography>
                        }
                        <Typography>Total cost: ${totalPrice}</Typography>
                    
                        <Typography
                          sx={{
                            marginTop: 2
                          }}
                        >
                          Refunds are available if the event is scheduled to occur at least 7 days into the future.
                        </Typography>
                    </DialogContentText>
                  </DialogContent>
                  <DialogActions>
                    <Button onClick={handleDialogClose}>Cancel</Button>
                    <Button onClick={handleConfirmButton}>Confirm</Button>
                  </DialogActions>
                </Dialog>

              </Box>
            )}

            {host === true && 
              <Box
              sx={{
                width: 400,
                display: 'flex',
                justifyContent: 'flex-end',
                flexDirection: 'column',
                boxShadow: "0px 6px 16px rgba(0, 0, 0, 0.12)",
                padding: 2,
                marginLeft: 10
              }}
              >
                <Button
                  variant="text"
                  sx={{
                    color: 'black',
                    fontSize: '24px',
                    width: '100%',
                    marginBottom: 1,
                    display: 'flex',
                    justifyContent: 'flex-start',
                    '&:hover': {
                      backgroundColor: 'lightgrey',
                    },
                  }}
                  onClick={handleInsightsNavigation}
                >
                  <InsightsIcon sx={{ marginRight: 2 }} />
                  Event Insights
                </Button>
                <BroadcastButton 
                  token={userObj.user.token}
                  event_id={eventId}
                />
                {isTimeBefore && (
                  <CancelButton
                    token={userObj.user.token}
                    title={title}
                    event_id={eventId}
                    handleSuccess={handleSuccess}
                    handleError={handleError}
                  />
                )}
              </Box>
            }

          </Box>
          
        </Box>

      </React.Fragment>
    </ThemeProvider>
  )
}

export default EventPage
