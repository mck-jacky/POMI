import React, { useState, useContext, useEffect } from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Backdrop from '@mui/material/Backdrop';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import { fetchURL } from '../../../../helper';

const CancelButton = ({ token, title, event_id, handleSuccess, handleError }) => {
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false)
  const [processing, setProcessing] = React.useState(false);

  const handleCancelEvent = async () => {
    setProcessing(true)
    try {
      const res = await fetchURL('event/cancel', 'POST', {
        token: token,
        event_id: event_id,
      });
  
      console.log(res);
  
      handleSuccess("Cancelled Successfully.");
      setProcessing(false)
      setCancelDialogOpen(false)
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error(error);
      handleError(error)
      setProcessing(false)
      setCancelDialogOpen(false)
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <>
      <Button 
        variant="text"
        sx={{ 
          color: 'red',
          fontSize: '24px',
          width: '100%',
          marginBottom: 1,
          display: 'flex',
          justifyContent: 'flex-start',
          '&:hover': {
            backgroundColor: 'lightgrey',
          }
        }}
        onClick={() => setCancelDialogOpen(true)}
      >
        <CloseOutlinedIcon 
          sx={{ marginRight: 2 }}
        />
        Cancel
      </Button>

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
    </>
  )
}

export default CancelButton