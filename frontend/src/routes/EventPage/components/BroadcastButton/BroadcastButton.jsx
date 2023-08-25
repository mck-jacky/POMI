import React, { useState, useContext } from 'react'
import PodcastsIcon from '@mui/icons-material/Podcasts';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import { fetchURL } from '../../../../helper';
import Input from '@mui/material/Input';
import InputLabel from '@mui/material/InputLabel';
import InputAdornment from '@mui/material/InputAdornment';
import FormControl from '@mui/material/FormControl';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Backdrop from '@mui/material/Backdrop';

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const BroadcastButton = ({ token, event_id }) => {
  const [open, setOpen] = React.useState(false);
  const [subject, setSubjet] = React.useState('');
  const [body, setBody] = React.useState('');
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  const [showErrorAlert, setShowErrorAlert] = useState(false);
  const [errorMessage, setErrorMessage] = React.useState('Error')
  const [processing, setProcessing] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);

    setSubjet('')
    setBody('')
  };

  const handleSubjetChange = (event) => {
    setSubjet(event.target.value)
  }

  const handleBodyChange = (event) => {
    setBody(event.target.value)
  }

  async function handleSendButton (event) {
    if (subject === "" || body === "") {
      setErrorMessage("Email subject and Body cannot be empty")
      setShowErrorAlert(true)

      setTimeout(() => {
        setShowErrorAlert(false);
      }, 3000); 

      return
    }
    
    setProcessing(true)
    console.log(event_id)

    const res = await fetchURL('event/broadcast', 'POST', {
      token: token,
      event_id: event_id,
      email_subject: subject,
      message: body
    })

    try {
      if (res.code === 400 || res.code === 500) {
        setErrorMessage(res.message.replace(/<\/?p>/g, ''))
        setShowErrorAlert(true)

        setTimeout(() => {
          setShowErrorAlert(false);
        }, 3000);
      } else {
        setShowSuccessAlert(true)
        setSubjet('')
        setBody('')

        setTimeout(() => {
          setShowSuccessAlert(false);
        }, 3000);
      }
    } catch (error) {
      console.error(error)
    }

    setProcessing(false)
  }

  return (
    <>
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
          }
        }}
        onClick={handleClickOpen}
      >
        <PodcastsIcon 
          sx={{ marginRight: 2 }}
        />
        BROADCAST
      </Button>

      <Dialog
        open={open}
        TransitionComponent={Transition}
        keepMounted
        onClose={handleClose}
        aria-describedby="alert-dialog-slide-description"
        fullWidth
      >
        {showSuccessAlert && (
          <Alert severity="success">
            Broadcast message sent successfully to all attendees.
          </Alert>
        )}
        {showErrorAlert && (
          <Alert severity="error">
            {errorMessage}
          </Alert>
        )}

        {processing &&
          <Backdrop
            sx={{ color: '#fff', zIndex: 999 }}
            open={true}
          >
            <CircularProgress color="inherit" />
          </Backdrop>
        }

        <DialogTitle>{"Email / Broadcast"}</DialogTitle>
        <DialogContent>
          <FormControl variant="standard" fullWidth>
            <InputLabel htmlFor="input-with-icon-adornment">
              subject
            </InputLabel>
            <Input
              startAdornment={
                <InputAdornment position="start">
                </InputAdornment>
              }
              onChange={handleSubjetChange}
              value={subject}
            />
          </FormControl>
          <TextField
            label="Body"
            multiline
            rows={8}
            variant="standard"
            fullWidth
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                </InputAdornment>
              ),
            }}
            InputLabelProps={{
              shrink: true, // This ensures that the label moves up when the TextField is focused or filled
            }}
            sx={{
              marginTop: 2
            }}
            onChange={handleBodyChange}
            value={body}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>DISCARD</Button>
          <Button variant="contained" onClick={handleSendButton}>SEND</Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default BroadcastButton