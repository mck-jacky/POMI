import React, { useContext } from 'react'
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useNavigate } from 'react-router-dom';
import { fetchURL, formatTimeString } from '../../helper';
import { UserContext } from '../../userContext';

const Ticket2 = ({ name, time, location, tickets, id, handleSuccess, handleError }) => {
  const [open, setOpen] = React.useState(false);
  const [currTicket, setCurrTicket] = React.useState('')
  const userObj = useContext(UserContext);

  const navigate = useNavigate();

  const handleClickOpen = (ticket) => {
    setOpen(true);
    setCurrTicket(ticket)
  };

  const handleClose = () => {
    setOpen(false);
  };

  async function handleConfirmButton (event) {
    event.preventDefault();

    const res = await fetchURL('booking/cancel', 'POST', {
      token: userObj.user.token,
      event_id: id,
      ticket_code: currTicket.ticketId
    })

    console.log(res)

    if (res.code === 400) {
      handleError(res.message.replace(/<\/?p>/g, ''))
    } else {
      handleSuccess()
      console.log(res)
      setTimeout(() => {
        window.location.reload();
      }, 1000); // 1000 milliseconds = 1 second
    }

    setOpen(false)
  }


  return (
    <Accordion>
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls="panel1a-content"
        id="panel1a-header"
      >
        <Box>
          <Typography
            sx={{
              fontWeight: 'bold'
            }}
          >
            {name}
          </Typography>
          <Typography>{formatTimeString(time)}</Typography>
          <Typography>{location}</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
      <TableContainer component={Paper}>
        <Table 
          sx={{ 
            minWidth: 650,
            backgroundColor: '#99c5c4'
          }} 
          aria-label="simple table"
        >
          <TableHead>
            <TableRow>
            <TableCell align="center" sx={{ fontWeight: 'bold' }}>#TICKET ID</TableCell>
            <TableCell align="center" sx={{ fontWeight: 'bold' }}>SEAT</TableCell>
            <TableCell align="center" sx={{ fontWeight: 'bold' }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.map((row) => (
              <TableRow
                key={row.ticketId}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>{row.ticketId}</TableCell>
                {location === "Online" ? (
                  <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>N/A</TableCell>
                ) : (
                  <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>{row.ticketSeat}</TableCell>
                )}
                <TableCell 
                  align="center" 
                  sx={{ color: 'white', fontWeight: 'bold', cursor: 'pointer' }}
                  onClick={() => handleClickOpen(row)}
                >
                  CANCEL
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      </AccordionDetails>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          marginBottom: 2
        }}
      >
        <Button 
          variant="outlined"
          sx={{
            width: '95%',
            fontWeight: 'bold'
          }}
          onClick={() => navigate('/event/' + id)}
        >
          view event details
        </Button>

        <Dialog
          open={open}
          onClose={handleClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">
            Cancel Ticket <b>{currTicket.ticketId}</b> of <b>{name}</b>?
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              Eligible cancellations are for events 7 days away or more. Proceeding will refund your booking cost and free up your ticket for others.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={handleConfirmButton}>Confirm</Button>
          </DialogActions>
        </Dialog>
      </Box>

    </Accordion>
  )
}

export default Ticket2