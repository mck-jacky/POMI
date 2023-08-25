import React, { useState, useContext } from 'react'
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container } from '@mui/system';
import NavBar from '../../components/NavBar'
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Button from '@mui/material/Button';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import FmdGoodOutlinedIcon from '@mui/icons-material/FmdGoodOutlined';
import PermMediaOutlinedIcon from '@mui/icons-material/PermMediaOutlined';
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import LocalActivityOutlinedIcon from '@mui/icons-material/LocalActivityOutlined';
import MonetizationOnOutlinedIcon from '@mui/icons-material/MonetizationOnOutlined';
import NumbersOutlinedIcon from '@mui/icons-material/NumbersOutlined';
import CheckIcon from '@mui/icons-material/Check';
import { ToggleButtonGroup, ToggleButton } from '@mui/material';
import { DatePicker } from 'antd';
import { fetchURL, fileToDataUrl } from '../../helper'; 
import { useNavigate } from 'react-router-dom';
import Alert from '@mui/material/Alert';
import ArrowBackIosNewOutlinedIcon from '@mui/icons-material/ArrowBackIosNewOutlined';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import { UserContext } from '../../userContext';
import moment from 'moment';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';

const { RangePicker } = DatePicker;

const steps = [
  'Info',
  'Description',
  'Ticket',
];

const EventCreatePage = () => {
  const [step, setStep] = useState(1)
  const [eventTitle, setEventTitle] = React.useState('');
  const [organiser, setOrganiser] = React.useState('');
  const [category, setCategory] = React.useState('');
  const [locationType, setLocationType] = React.useState('');
  const [location, setLocation] = React.useState('');
  const [startTime, setStartTime] = React.useState('');
  const [endTime, setEndTime] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [ticketType, setTicketType] = React.useState('');
  const [price, setPrice] = React.useState('');
  const [quantity, setQuantity] = React.useState('');
  const [show, setShow] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [errorMessage, setErrorMessage] = useState('Error')
  const [image, setImage] = React.useState('');
  const [seatMap, setSeatMap] = React.useState('');
  const [minPrice, setMinPrice] = React.useState(0);
  const [maxPrice, setMaxPrice] = React.useState(0);

  const userObj = useContext(UserContext);
  const navigate = useNavigate();

  const handleEventTitleChange = (event) => {
    setEventTitle(event.target.value);
  };

  const handleOrganiserChange = (event) => {
    setOrganiser(event.target.value);
  };

  const handleCategoryChange = (event) => {
    setCategory(event.target.value);
  };

  const handleLocationTypeChange = (event) => {
    setLocationType(event.target.value);
    if (event.target.value === "Online" || event.target.value === "TBA") {
      setLocation(event.target.value)
    }
  };

  const handleLocationChange = (event) => {
    setLocation(event.target.value);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };

  const handleTicketTypeChange = (event, newOption) => {
    setTicketType(newOption);
    if (newOption === 'Free') {
      setPrice(0)
    }
  };

  const setShowErrorMessage = (message) => {
    setShow(true)
    setErrorMessage(message.replace(/<\/?p>/g, ''))
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const isValidNumber = (num) => {
    if (isNaN(num)) {
      // Input is not a valid number
      return false
    } else {
      // Input is a valid number
      return true
    }
  }

  function isTimeValid(time) {
    const now = moment();
    const diff = time.diff(now);
    
    return diff >= 0;
  }

  const handlePriceChange = (event) => {
    const priceInput = event.target.value;
    // Remove any non-digit or non-decimal characters from the input
    const filteredPriceInput = priceInput.replace(/[^\d.]/g, '');
    setPrice(filteredPriceInput);
    setMinPrice(filteredPriceInput);
    setMaxPrice(filteredPriceInput);
  };

  const handleMinPriceChange = (event) => {
    const priceInput = event.target.value;
    // Remove any non-digit or non-decimal characters from the input
    const filteredPriceInput = priceInput.replace(/[^\d.]/g, '');
    setPrice(filteredPriceInput)
    setMinPrice(filteredPriceInput);
  }

  const handleMaxPriceChange = (event) => {
    const priceInput = event.target.value;
    // Remove any non-digit or non-decimal characters from the input
    const filteredPriceInput = priceInput.replace(/[^\d.]/g, '');
    setMaxPrice(filteredPriceInput);
  }

  const handleQuantityChange = (event) => {
    const input = event.target.value;
    // Remove any non-digit characters from the input
    const filteredInput = input.replace(/\D/g, '');
    setQuantity(filteredInput);
  };

  async function handleNextClick () {
    if (step === 1) {
      if (eventTitle === "") {
        setShowErrorMessage("Event title cannot be empty")
      } else if (organiser === "") {
        setShowErrorMessage("Organiser cannot be empty")
      } else if (category === "") {
        setShowErrorMessage("Category cannot be empty")
      } else if (locationType === "") {
        setShowErrorMessage("Location type cannot be empty")
      } else if (location === "") {
        setShowErrorMessage("Location cannot be empty")
      } else if (range === null) {
        setShowErrorMessage("Location cannot be empty")
      } else if (startTime === "" || endTime === "") {
        setShowErrorMessage("Time cannot be empty") 
      } else if (!isTimeValid(moment(startTime)) || !isTimeValid(moment(endTime))) {
        setShowErrorMessage("Please enter a valid time") 
      }
      else {
        setShow(false)
        setActiveStep((prevActiveStep) => prevActiveStep + 1);
        setStep(step + 1); 
      }
    } else if (step === 2) {
        if (description === "") {
          setShowErrorMessage("Description cannot be empty")
        } else {
          window.scrollTo({ top: 0, behavior: 'smooth' });
          setShow(false)
          setActiveStep((prevActiveStep) => prevActiveStep + 1);
          setStep(step + 1);
        }
    } 
  };

  const handleBackClick = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    setStep(step - 1);
  }

  const imageOnChange = async (e) => {
    const bufferData = await fileToDataUrl(e.target.files[0])
    setImage(bufferData)
  }

  const seatMapOnChange = async (e) => {
    const seatMapBufferData = await fileToDataUrl(e.target.files[0])
    setSeatMap(seatMapBufferData)
  }

  async function handleSubmit (event) {
    event.preventDefault();

    if (ticketType === "") {
      setShowErrorMessage("Please choose a ticket type")
      return
    } else if (price === "" || isValidNumber(price) === false) {
      setShowErrorMessage("Please enter a valid price")
      return
    } else if (quantity === "" || isValidNumber(quantity) === false || quantity < 1) {
      setShowErrorMessage("Please enter a valid quantity")
      return
    } else if (parseFloat(minPrice) > parseFloat(maxPrice)) {
      setShowErrorMessage("Minimum Price cannot be greater than Maximum Price")
      return
    } else if (DynamicPricingIsChecked === false) {
      setMinPrice(price)
      setMaxPrice(price)
    }

    const res = await fetchURL('event/create', 'POST', {
      token: userObj.user.token,
      event_title: eventTitle,
      event_description: description,
      event_type: category,
      venue: location,
      venue_type: locationType,
      organiser: organiser,
      start_date_time: moment(startTime).format('YYYY MM DD HH mm ss'),
      end_date_time: moment(endTime).format('YYYY MM DD HH mm ss'),
      num_tickets_available: quantity, 
      tickets_left: quantity,
      ticket_price: price,
      image: image,
      number_of_seats: quantity,
      seating_plan_image: seatMap,  
      price_min: minPrice,
      price_max: maxPrice
    })


    console.log(res)

    if (res.code === 400) {
      setShow(true)
      setErrorMessage(res.message)
    } else {
      setShowSuccess(true)

      window.scrollTo({ top: 0, behavior: 'smooth' });

      setTimeout(() => {

        setShow(false)
        setShowSuccess(false)
        navigate('/');
      }, 3000);
    }
  }

  const [range, setRange] = useState(null)
  const onChange = (value, dateString) => {
    setRange(value)
    setStartTime(dateString[0])
    setEndTime(dateString[1])
  };

  const [activeStep, setActiveStep] = React.useState(0);

  const [DynamicPricingIsChecked, setDynamicPricingIsChecked] = useState(false);

  const handleDynamicPricingCheckBox = (event) => {
    setPrice("")
    setMinPrice("")
    setMaxPrice("")
    setDynamicPricingIsChecked(event.target.checked);
  };

  return (
    <React.Fragment>
      <NavBar />
      {showSuccess &&
        <Alert icon={<CheckIcon fontSize="inherit" />} severity="success">
          Creation successful. You will be automatically redirected in 3 seconds...
        </Alert>
      }
      {show &&
        <Alert severity='error' onClose={() => setShow(false)}>{errorMessage}</Alert>
      }
      <CssBaseline />
      <Container maxWidth="sm">
        <Box
          sx={{
            marginTop: 7,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >

        <Typography component="h1" variant="h3" sx={{ marginBottom: 3 }}>
          {step > 1 && (
            <ArrowBackIosNewOutlinedIcon
              sx={{
                fontSize: '2rem', // Adjust the font size to make the icon bigger
                marginRight: '0.5rem', // Adjust the margin right as needed
                cursor: 'pointer'
              }}
              onClick={handleBackClick}
            />
          )}
          
          Create new event
        </Typography>

        <Box sx={{ width: '100%' }}>
          <Stepper activeStep={activeStep}>
            {steps.map((label, index) => {
              const stepProps = {};
              const labelProps = {};
              return (
                <Step key={label} {...stepProps}>
                  <StepLabel {...labelProps}>{label}</StepLabel>
                </Step>
              );
            })}
          </Stepper>
        </Box>

        <Box
          sx={{
            marginTop: 5,
          }}
        />

        {step === 1 && (
          <Box sx={{width: '100%'}}>
      
            <Typography variant='h4'>
            <InfoOutlinedIcon
              sx={{
                fontSize: '2rem', // Adjust the font size to make the icon bigger
                marginRight: '0.5rem', // Adjust the margin right as needed
              }}
            />
              Basic Info
            </Typography>

            <Typography variant='subtitle1'>
              Name your event. Add details that highlight what makes it unique.
            </Typography>

            <TextField
              value={eventTitle}
              onChange={handleEventTitleChange}
              margin="normal"
              required
              fullWidth
              id="event-create-event-title"
              label="Event Title"
              name="Event Title"
              inputProps={{ 'aria-label': 'Event Title' }}
              />

            <TextField
              value={organiser}
              onChange={handleOrganiserChange}
              margin="normal"
              required
              fullWidth
              id="event-create-organiser"
              label="Organiser"
              name="Organiser"
              inputProps={{ 'aria-label': 'Organiser' }}
              />

            <FormControl fullWidth margin='normal'>
              <InputLabel>Category *</InputLabel>
              <Select
                value={category}
                label="Category"
                onChange={handleCategoryChange}
              >
                <MenuItem value={'Music'}>Music</MenuItem>
                <MenuItem value={'Performing & Visual Arts'}>Performing & Visual Arts</MenuItem>
                <MenuItem value={'Seasonal'}>Seasonal</MenuItem>
                <MenuItem value={'Health'}>Health</MenuItem>
                <MenuItem value={'Hobbies'}>Hobbies</MenuItem>
                <MenuItem value={'Business'}>Business</MenuItem>
                <MenuItem value={'Food & Drink'}>Food & Drink</MenuItem>
                <MenuItem value={'Sports & Fitness'}>Sports & Fitness</MenuItem>
              </Select>
            </FormControl>

            <Typography variant='h4'>
              <FmdGoodOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Location
            </Typography>

            <Typography variant='subtitle1'>
              Help people in the area discover your event and let attendees know where to show up.
            </Typography>

            <FormControl fullWidth margin='normal'>
              <InputLabel id="demo-simple-select-label">Location *</InputLabel>
              <Select
                id="event-create-location-type"
                value={locationType}
                label="Location Type"
                onChange={handleLocationTypeChange}
              >
                <MenuItem value={'Venue'}>Venue</MenuItem>
                <MenuItem value={'Online'}>Online</MenuItem>
                {/* <MenuItem value={'TBA'}>TBA</MenuItem> */}
              </Select>
            </FormControl>

            <TextField
              value={location}
              onChange={handleLocationChange}
              margin="normal"
              required
              fullWidth
              id="event-create-location"
              label="Search for an address"
              name="Search for an address"
              inputProps={{ 'aria-label': 'Location' }}
              disabled={locationType === 'Online' || locationType === "TBA"}
              />

            <Typography variant='h4'>
              <InfoOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Time
            </Typography>

            <Typography variant='subtitle1'>
                Tell event-goers when your event starts and ends so they can make plans to attend.
            </Typography>

            <Box sx={{marginTop: 1, marginBottom: 1}}>
              <RangePicker
                showTime={{
                  format: 'HH:mm',
                }}
                format="YYYY-MM-DD HH:mm"
                onChange={onChange}
                value={range}
              />

            </Box>

            <Box
              sx={{
                marginTop: 10,
                display: 'flex',
                justifyContent: 'flex-end'
              }}
            >
              <Button onClick={handleNextClick}>Next</Button>
            </Box>
            
          </Box>
        )}

        {step === 2 && (
          <Box sx={{width: '100%'}}>
            <Typography variant='h4'>
              <PermMediaOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Images
            </Typography>

            <Typography variant='subtitle1'>
                Add photos to show what your event be about.
            </Typography>
            
            <Button
                variant="contained"
                component="label"
                sx={{
                  marginBottom: 3
                }}
              >
                Upload Images
                <input
                  id="image-upload"
                  name="image-thumbnail"
                  type="file"
                  accept="image/*"
                  aria-label="Upload image thumbnail"
                  onChange={imageOnChange}
                  // multiple
                  hidden
                />
            </Button>

            {image && (
                <>
                  <Button
                    sx={{ 
                      marginLeft: '10px', 
                      marginTop: '-23px'
                    }}
                    variant="contained"
                    component="label"
                    aria-label="Remove image"
                    onClick={ () => setImage('') }
                  >Remove</Button>
                  <Box sx={{ marginTop: '10px' }}>
                    <img
                      src={image}
                      width='250'
                      alt='thumbnail'
                    >
                    </img>  
                  </Box>
                </>
            )}

            <Typography variant='h4'>
              <DescriptionOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Description
            </Typography>

            <Typography variant='subtitle1'>
                Grap people's attention with a short description about your event.
            </Typography>

            <TextField
              value={description}
              onChange={handleDescriptionChange}
              margin="normal"
              required
              fullWidth
              multiline
              rows={5}
              id="event-create-description"
              label="What is your event about?"
              name="Description"
              inputProps={{ 'aria-label': 'Description' }}
              />
            <Box
              sx={{
                marginTop: 10,
                display: 'flex',
                justifyContent: 'flex-end'
              }}
            >
              <Button onClick={handleNextClick}>Next</Button>
            </Box>
          </Box>   
        )}

        {step === 3 && (
          <Box sx={{width: '100%'}} component="form" onSubmit={handleSubmit}>
            <Typography variant='h4'>
              <PermMediaOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Seat map
            </Typography>

            <Typography variant='subtitle1'>
              Upload a seat map for events with designated seating; not required for general admission.
            </Typography>
            
            <Button
              variant="contained"
              component="label"
              sx={{
                marginBottom: 3
              }}
            >
              Upload Images
              <input
                id="image-upload"
                name="image-thumbnail"
                type="file"
                accept="image/*"
                aria-label="Upload image thumbnail"
                onChange={seatMapOnChange}
                // multiple
                hidden
              />
          </Button>

            {seatMap && (
                <>
                  <Button
                    sx={{ 
                      marginLeft: '10px', 
                      marginTop: '-23px'
                    }}
                    variant="contained"
                    component="label"
                    aria-label="Remove image"
                    onClick={ () => setSeatMap('') }
                  >Remove</Button>
                  <Box sx={{ marginTop: '10px' }}>
                    <img
                      src={seatMap}
                      width='250'
                      alt='thumbnail'
                    >
                    </img>  
                  </Box>
                </>
              )}

            <Typography variant='h4'>
              <LocalActivityOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Ticket
            </Typography>
            <Typography variant='subtitle1'>
                Choose a ticket type.
            </Typography>
            <ToggleButtonGroup
              value={ticketType}
              exclusive
              onChange={handleTicketTypeChange}
              sx={{
                marginTop: 1.5,
                marginBottom: 1.5 
              }}
            >
              <ToggleButton
                value="Paid"
                sx={{
                  width: '200px', // Adjust the desired width here
                }}
              >
                Paid
              </ToggleButton>
              <ToggleButton
                value="Free"
                sx={{
                  width: '200px', // Adjust the desired width here
                }}
              >
                Free
              </ToggleButton>
            </ToggleButtonGroup>
            <Typography variant='h4'>
              <MonetizationOnOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Price
            </Typography>
            
            {(DynamicPricingIsChecked && ticketType === 'Paid') ? (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between"
                }}
              >
                <TextField
                  sx={{
                    width: "48%"
                  }}
                  value={minPrice}
                  onChange={handleMinPriceChange}
                  margin="normal"
                  required
                  label="Minimum Price"
                  name="Minimum Price"
                  inputProps={{ 'aria-label': 'Price' }}
                />
                <TextField
                  sx={{
                    width: "48%"
                  }}
                  value={maxPrice}
                  onChange={handleMaxPriceChange}
                  margin="normal"
                  required
                  label="Maximum Price"
                  name="Maximum Price"
                  inputProps={{ 'aria-label': 'Price' }}
                />
              </Box>
            ) : (
              <TextField
                value={price}
                onChange={handlePriceChange}
                margin="normal"
                required
                fullWidth
                id="event-create-price"
                label="Price"
                name="Price"
                inputProps={{ 'aria-label': 'Price' }}
                disabled={ticketType === 'Free'}
              />
            )}
            
            {ticketType === 'Paid' && (
              <FormControlLabel
                control={<Checkbox checked={DynamicPricingIsChecked} onChange={handleDynamicPricingCheckBox} />}
                label="Dynamic Pricing"
              />
            )}

            <Typography variant='h4'>
              <NumbersOutlinedIcon
                sx={{
                  fontSize: '2rem', // Adjust the font size to make the icon bigger
                  marginRight: '0.5rem', // Adjust the margin right as needed
                }}
              />
              Quantity
            </Typography>
            
            <TextField
              value={quantity}
              onChange={handleQuantityChange}
              margin="normal"
              required
              fullWidth
              id="event-create-quantity"
              label="Quantity"
              name="Quantity"
              inputProps={{ 'aria-label': 'Quantity' }}
              />

            <Box
              sx={{
                marginTop: 10,
                display: 'flex',
                justifyContent: 'flex-end'
              }}
            >
              
              <Button type='submit'>Create</Button>
            </Box>
          </Box> 
        )}

      
      </Box>
      </Container>
    </React.Fragment>
  );
}

export default EventCreatePage
