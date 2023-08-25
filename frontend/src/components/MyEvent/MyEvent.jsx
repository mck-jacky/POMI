import React, { useState, useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { fetchURL } from '../../helper';
import MenuIcon from '@mui/icons-material/Menu';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import { UserContext } from '../../userContext';
import { useNavigate } from 'react-router-dom';
import { formatTimeString } from '../../helper';
import Backdrop from '@mui/material/Backdrop';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';

const MyEvent = ({ id, title, time, location, image, handleSuccess, handleError }) => {
  const userObj = useContext(UserContext);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const navigate = useNavigate();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [emailSubject, setEmailSubject] = useState('');
  const [message, setMessage] = useState('');
  const [dialogMode, setDialogMode] = useState(null); 
  const [broadcastDialogOpen, setBroadcastDialogOpen] = useState(false);
  const [broadcastEmailSubject, setBroadcastEmailSubject] = useState('');
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false)
  const [processing, setProcessing] = React.useState(false);
  const [broadcastErrorMessage, setBroadcastErrorMessage] = useState('');
  const [broadcastShowError, setBroadcastShowError] = useState(false);
  const [broadcastSuccess, setBroadcastSuccess] = useState(false);
  const [broadcastSuccessMessage, setBroadcastSuccessMessage] = useState('');
  const abortController = React.useRef(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleAlertClose = () => {
    setTimeout(() => {
      setBroadcastSuccess(false);
    }, 5000);
  };

  const handleDialogOpen = () => {
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    handleClose();
  };

  const handleBroadcast = () => {
    setDialogMode('broadcast');
    setBroadcastDialogOpen(true);
    handleClose();
  };

  time = formatTimeString(time)

  const handleCancelEvent = async () => {
    setProcessing(true)
    try {
      const res = await fetchURL('event/cancel', 'POST', {
        token: userObj.user.token,
        event_id: id,
      });
  
      console.log(res);
  
      handleClose();
      handleSuccess();
      setProcessing(false)
      setCancelDialogOpen(false)
      window.location.reload();
    } catch (error) {
      console.error(error);
      setProcessing(false)
      setCancelDialogOpen(false)
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    if (broadcastSuccess) {
      setTimeout(() => {
        handleClose();
        setBroadcastDialogOpen(false);
      }, 2000); // close the dialog after 5 seconds
    }
  }, [broadcastSuccess]);

  let alertTimeout = null; 
  
  const handleConfirmButton = async (event) => {
    event.preventDefault();

    abortController.current = new AbortController();

    setTimeout(() => {
      setDialogOpen(false);
    }, 5000);
  
    setProcessing(true)
  
    if (dialogMode === 'cancel') {
      // Handle cancellation logic
    } else if (dialogMode === 'broadcast') {
      try {
        const res = await fetchURL('event/broadcast', 'POST', {
          token: userObj.user.token,
          event_id: id,
          message: message,
          email_subject: emailSubject,
        }, { signal: abortController.current.signal }); 
  
        console.log(res);
  
        if (res && res.success) {
          setBroadcastSuccess(true);
          setBroadcastSuccessMessage("Your message has been successfully sent!");
          clearTimeout(alertTimeout);
          alertTimeout = setTimeout(() => {
            setBroadcastSuccess(false);
          }, 5000);
        } else if (res && res.message) {
          const errorMessage = res.message.replace(/<\/?p>/gi, '');
          setBroadcastErrorMessage(errorMessage);
          setBroadcastShowError(true);
        } else {
          setBroadcastErrorMessage("An error occurred while sending your message.");
          setBroadcastShowError(true);
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('Fetch aborted');
          throw error;
        } else {
          console.error(error);
        }
      }
    }
    setProcessing(false);
  };
  
  if (image === '') {
    image =
      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAC3CAMAAAAGjUrGAAAAM1BMVEXp7vG6vsHs8fS3u77Fycy+wsXc4eTX3N/h5unT2NrHzM7N0tW1ubzu8/W7v8LBxcjl6uwx8f6JAAADy0lEQVR4nO2c23aDIBBFCQheUf//a6vRpEZuJgXj0LNXH7oaK3WXwXEQGAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGnw9Hz7Et+Ds1ElpxoJaeGsHHqRHlkoKlJ0JbvbKQhRjCSs8FKcY+RuRVKQwqsTlUxShm9f8BGGU53cuvryHeXUyLnTj9++5hC8WJ2kv+2sTkR79Y4y9uuf2papKVYnxcWd8GpV0uj0aaxcnFx9lH04ESeMfLpZ2pLJW/obZzrhcGK2BSdmW3BitkXdyfxYz7mO2hZtJ7yqCznIoVUsXv8h7YSPzZJ2CtENZTQplJ1Mj0CbZ6CuiFUdI+yEt69PhUJGih+6Tni5L7qJJlJbZJ2MZu1A1FHuP2Sd7CPnTh+nLapOKtNIrIyOqhNe28puYvjXThp7KfKAE16FDqDqxF6x7sI1VK26wFCcmRMR6gOTEhG6P+XmJNRPtJrruqL0SSHrxD6ehJxwtZS6vVLIOrFP9wTuO1o95XnCh6qTj/ITrsSRQ8k6Ydbg8YYOV9tDhbO4QNaJbUrd301elXikkHUyZbLGc7F34m4bOI9z2ccUuk6Ybl+liMFXP9GGEme/IuxkfubZXKcofL+vVW8ocYUPZSfThRbdYkUIWftKj3YljjyFtBPGtWplL259UzJfZmoLHPeYQtvJMr0zjsxfnnYrsY4p1J0c+l1H4DzOaByfv5N9XhLsKfk7MfOSkJTsnYSVGANt7k50IHBsZ83ciSsv8faUjJxw821w303YLSUfJ7q+VbvPjit5eRs2Gyfzw0//usTkaODsz5yLk6mXTPTbnhLKS5xSMnGyKJnnMn4j4I3AWeie9e8cnGxmSh/h876S55CShZNtEX8Nn3eG1xyd6Nf59FnKsVQtXyf7qR5R6U96SU5OLG9dVB8pyceJbUJQvpOX5OdElx9dfs5OdMxVgnk4ibtwMgsnvI5oJA8nMceSTJxEHUvycBJ/ETZ5JwnWpZN3Yn1n+H874RJODr4LCidwAic74MQETkzgxAROTODEBE5MzDy2i763VEfcCVOlmr+UMr8J/8DxybpIjKyTlG3BidkWnJhtwYnZFpyYbcGJ2VZBwwkb18SqV6lb4usUyeX3NmTrJozzvy81j7S2Sd8l/4a27XeSFHH5jbqfG4OexvVDx7HjSTqu300Y+91p+BS6NuregKnQjn1gEiBCe6RcBl7K6AUCO0VFRMm89EK1RXKatoq4e+QJJN+N+r4jNQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzuIHpk8/wVCHmdcAAAAASUVORK5CYII=';
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginBottom: 2
      }}
    >

      <Box
        sx={{
          width: 850,
          display: 'flex',
          padding: 2,
          position: 'relative',
          backgroundColor: 'rgba(0, 0, 0, 0.5)'
        }}
      >
        <Box
          sx={{
            width: '100%',
            height: '100%',
            position: 'absolute',
            top: 0,
            left: 0,
            backgroundImage: `url(${image})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'blur(5px)', // Adjust the blur intensity as needed
            zIndex: -1,
          }}
        />

        <Box
          component="img"
          sx={{
            width: 205,
            height: 115,
            maxWidth: 205,
            maxHeight: 115
          }}
          alt='event-image'
          src={image}
        />

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            marginLeft: 2,
            justifyContent: 'center',
            color: 'white',
            width: 600,
          }}
        >
          <Typography
            sx={{
              fontSize: 16,
              fontWeight: 800,
            }}
          >
            {title}
          </Typography>
          <Typography
            sx={{
              fontSize: 16,
              fontWeight: 700,
            }}
          >
            {time} | {location}
          </Typography>
        </Box>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}
        >
          <Button
            title="Cancel"
            sx={{
              '&:hover': {
                '& .hover-text': {
                  display: 'block',
                },
              },
            }}
            onClick={handleClick}
          >
            <MenuIcon
              sx={{
                fontSize: 25,
                color: 'white',
              }}
            />
            <span className="hover-text" style={{ display: 'none' }}>
              Menu
            </span>
          </Button>
          <Menu
            id="basic-menu"
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            MenuListProps={{
              'aria-labelledby': 'basic-button',
            }}
          >
            <MenuItem onClick={handleBroadcast}>Broadcast</MenuItem>
            <Link to={`/event_insights/${id}`}>
              <MenuItem onClick={handleClose}>Insights</MenuItem>
            </Link>
            <MenuItem onClick={() => setCancelDialogOpen(true)}>Cancel</MenuItem>
          </Menu>
        </Box>

      </Box>

      <Dialog
        open={cancelDialogOpen}
        onClose={() => setCancelDialogOpen(false)}
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
          Cancel <b>{title}</b>?
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            <Typography
              sx={{
                marginBottom: 2
              }}
            >
                Are you sure you want to cancel this event? Please note that the following actions will occur upon confirmation:
              </Typography>
              <Typography>1. All current event bookings will be automatically cancelled.</Typography>
              <Typography>2. A cancellation message will be sent to all customers with a booking.</Typography>
              <Typography>3. Booking costs will be refunded to all customers.</Typography>
          
              <Typography
                sx={{
                  marginTop: 2
                }}
              >
                <b>These actions cannot be undone.</b>
              </Typography>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCancelEvent}>Confirm</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={broadcastDialogOpen}
        onClose={() => setBroadcastDialogOpen(false)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          <b>Event Broadcast</b>
        </DialogTitle>
        {broadcastShowError ? (
          <Alert severity="error" onClose={() => setBroadcastShowError(false)}>
            {broadcastErrorMessage}
          </Alert>
        ) : broadcastSuccess ? (
          <Alert severity="success" onClose={handleAlertClose}>
            {broadcastSuccessMessage}
          </Alert>
        ) : null}
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            <Typography variant="subtitle1">Email Subject:</Typography>
            <input
              type="text"
              value={emailSubject}
              onChange={(e) => setEmailSubject(e.target.value)}
              style={{ marginBottom: '16px' }}
            />

            <Typography variant="subtitle1">Message:</Typography>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              style={{ height: '100px', marginBottom: '16px', resize: 'vertical' }}
            />
          </DialogContentText>
          {processing && (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              mt={2}
            >
              <CircularProgress />
            </Box>
          )}

        </DialogContent>
        <DialogActions>
          <Button onClick={() => { 
            if (abortController.current) abortController.current.abort(); 
            setBroadcastDialogOpen(false); 
          }}>
            Cancel
          </Button>
          <Button onClick={handleConfirmButton} disabled={processing}>
            {processing ? "Sending..." : "Send"}
          </Button>
        </DialogActions>
      </Dialog>

    </Box>
  );
};

export default MyEvent;