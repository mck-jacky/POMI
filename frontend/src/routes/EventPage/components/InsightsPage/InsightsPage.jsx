import React, { useContext, useEffect, useState } from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import NavBar from '../../../../components/NavBar';
import { UserContext } from '../../../../userContext';
import { fetchURL } from '../../../../helper';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { useParams } from 'react-router';
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Cell } from 'recharts';

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

const InsightsPage = () => {
  const userObj = useContext(UserContext);
  const { eventId } = useParams();
  const [email, setEmail] = useState("");
  const [actualAttendance, setActualAttendance] = useState("");
  const [isEventCreatedPast, setIsEventCreatedPast] = useState(false); // New state for checking if event is created in the past
  const [isEventCreatedFuture, setIsEventCreatedFuture] = useState(false);
  const [error, setError] = useState(null);
  const [pastAttendancePrediction, setPastAttendancePrediction] = useState(null);
  const [currentAttendancePrediction, setCurrentAttendancePrediction] = useState(null);
  const [trueAttendance, setTrueAttendance] = useState(null);
  const [eventDetails, setEventDetails] = useState(null);
  const [success, setSuccess] = useState(null);
  const [predictedDemand, setPredictedDemand] = useState(null);

  const handleCheckEventCreatedPast = async () => {
    try {
      const res = await fetchURL('user/events/created/past', 'POST', {
        input_email: userObj.user.email,
      });

      const eventIds = res.map((event) => event.event_id);
      const isEventInPast = eventIds.includes(parseInt(eventId));
      const event = res.find((event) => event.event_id === parseInt(eventId));

      if (res.length > 0 && isEventInPast) {
        setIsEventCreatedPast(true);
        setEventDetails(event);
      } else {
        setIsEventCreatedPast(false);
      }
    } catch (error) {
      console.error(error);
      setTimeout(() => {
        throw error;
      }, 5000); // Log the error for 5 seconds before rethrowing it
    }
  };

  const handleCheckEventCreated = async () => {
    try {
      const res = await fetchURL('user/events/created', 'POST', {
        input_email: userObj.user.email,
      });
      const eventIds = res.map((event) => event.event_id);
      const isEventInFuture = eventIds.includes(parseInt(eventId));
      const event = res.find((event) => event.event_id === parseInt(eventId));

      if (res.length > 0 && isEventInFuture) {
        setIsEventCreatedFuture(true);
        setEventDetails(event);
      } else {
        setIsEventCreatedFuture(false);
      }
    } catch (error) {
      console.error(error);
      setTimeout(() => {
        throw error;
      }, 5000); // Log the error for 5 seconds before rethrowing it
    }
  };

  useEffect(() => {
    setEmail(userObj.user.email);
    handleCheckEventCreatedPast();
    handleCheckEventCreated();
  
    if (isEventCreatedPast) {
      getAttendancePredictionPast();
      getHistoricalAttendance();
    } else if (isEventCreatedFuture) {
      getAttendancePredictionCurrent();
      getForecastDemand();
    }
  }, [isEventCreatedPast, isEventCreatedFuture]);

  // Past event stuff
  const handleUpdateAttendance = async (e) => {
    e.preventDefault();
    setError(null); // Reset the error state before making the API call

    try {
      const res = await fetchURL('update/attendance', 'POST', {
        event_id: eventId,
        actual_attendance: actualAttendance,
      });

      if ("success" in res) {
        // Display the success message
        setSuccess(res.success);
        console.log(res.success);
      } else if ("error" in res) {
        // Display the error message from the backend on the page
        setError(res.error);
      } else {
        console.log('Unexpected response from the server.');
      }
    } catch (error) {
      console.error(error);
      setError('An unexpected error occurred.'); // Set a generic error message for network errors, etc.
    }
  };

  const getAttendancePredictionPast = async () => {
    try {
      const res = await fetchURL('attendance/prediction/past', 'POST', {
        event_id: eventId,
      });
      console.log(res)
      if (!res) {
        // Handle the case when the response is null (API call failed)
        console.error('Error: Failed to fetch data for past event.');
        return;
      }

      setPastAttendancePrediction(parseFloat(res));
      console.log(parseFloat(res));
      
    } catch (error) {
      console.error(error);
    }
  };

  const getHistoricalAttendance = async () => {
    try {
      const res = await fetchURL('get/historical/attendance', 'POST', {
        event_id: eventId,
      });
      console.log(eventId)
      if (!res) {
        // Handle the case when the response is null (API call failed)
        console.error('Error: Failed to fetch data for past event.');
        return;
      }

      setTrueAttendance(res);
      console.log(res);
      
    } catch (error) {
      console.error(error);
    }
  };

  // Curr event stuff
  const getAttendancePredictionCurrent = async () => {
    try {
      const res = await fetchURL('attendance/prediction/current', 'POST', {
        event_id: eventId,
      });
      console.log(res);
      if (res === null) {
        // Handle the case when the response is null (API call failed)
        console.error('Error: Failed to fetch data for current event.');
        return;
      }
      setCurrentAttendancePrediction(parseFloat(res));
      console.log(parseFloat(res));
    } catch (error) {
      console.error(error);
    }
  };

  const getForecastDemand = async () => {
    console.log(typeof(eventId))
    try {
      const res = await fetchURL('forecast/demand', 'POST', {
        event_id: eventId,
      });
      console.log(res)
      if (!res) {
        console.error('Error: Failed to fetch forecast demand.');
        return;
      }
      
      setPredictedDemand(parseFloat(res));
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <React.Fragment>
        <NavBar />
        {isEventCreatedPast && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '10vh' }}>
            {/* Render content when event is created in the past */}
            <h1>Past Event Insights</h1>
          </div>
        )}
        {isEventCreatedFuture && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px' }}>
            {/* Render current event */}
            <h1 style={{ marginBottom: '20px' }}>Upcoming Event Insights</h1>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '20px', border: '1px solid #ddd', borderRadius: '5px', maxWidth: '1200px', marginTop: '40px' }}>
              <div style={{ flex: 1, textAlign: 'center', padding: '20px' }}>
                <h2 style={{ marginBottom: '15px' }}>{eventDetails.event_title}</h2>
                <p><strong>Event Type:</strong> {eventDetails.event_type}</p>
                <p><strong>Host:</strong> {eventDetails.host}</p>
                <p><strong>Event Description:</strong> {eventDetails.event_description}</p>
                <p><strong>Ticket Price:</strong> {eventDetails.price_max}</p>

                {/* Add the prediction commentary */}
                <p>Our model predicts that <strong>{Math.min(Math.ceil(currentAttendancePrediction), predictedDemand)}</strong> people will attend the event.</p>
              </div>

              {/* BarChart */}
                <div style={{ flex: 1, padding: '20px' }}>
                    <BarChart width={900} height={300} data={[
                      { name: 'Tickets Sold', value: eventDetails.num_tickets_available - eventDetails.num_tickets_left, fill: '#99c5c4' },
                      { name: 'Total tickets available', value: eventDetails.num_tickets_available, fill: '#d3ebeb' },
                      { name: 'Current Attendance Prediction', value: Math.min(currentAttendancePrediction, predictedDemand), fill: '#99c5c4' },
                      { name: 'Predicted Demand', value: predictedDemand, fill: '#d3ebeb' },
                    ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => value} /> {/* Display the value as is */}
                    <Bar dataKey="value">
                      {
                        // Render different colors for each bar
                        (data) => data.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))
                      }
                    </Bar>
                  </BarChart>

                <p style={{ fontSize: '12px', fontStyle: 'italic', color: 'gray', marginTop: '20px', textAlign: 'center' }}>
                  * Disclaimer: Please rely on these figures at your own risk. Although we thrive to produce accurate
                  results, there are inevitable discrepancies. Hence, we will not be responisble for any consequences 
                  arising from using this data.</p>
              </div>
            </div>
          </div>
        )}

        {isEventCreatedPast && !isEventCreatedFuture && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '20px', border: '1px solid #ddd', borderRadius: '5px', maxWidth: '1200px', marginTop: '40px' }}>
              <div style={{ flex: 1, textAlign: 'center', padding: '20px' }}>
                <h2 style={{ marginBottom: '15px' }}>{eventDetails.event_title}</h2>
                <p><strong>Event Type:</strong> {eventDetails.event_type}</p>
                <p><strong>Host:</strong> {eventDetails.host}</p>
                <p><strong>Event Description:</strong> {eventDetails.event_description}</p>
                <p><strong>Ticket Price:</strong> {eventDetails.price_max}</p>
                <p>Please input the actual attendance number</p>
                <div>
                  <form onSubmit={handleUpdateAttendance}>
                    <TextField
                      label="Actual Attendance"
                      value={actualAttendance}
                      onChange={(e) => setActualAttendance(e.target.value)}
                      required
                    />
                    <Button type="submit" variant="contained" color="primary">
                      Update Attendance
                    </Button>
                  </form>
                </div>
                {error && <div style={{ color: 'red' }}>{error}</div>} {/* Display error message if there's an error */}
                {success && <div style={{ color: 'green' }}>{success}</div>} {/* Display success message if there's a success */}
              </div>

              {/* BarChart */}
              <div style={{ flex: 1, padding: '20px' }}>
              <BarChart width={800} height={300} data={[
                { name: 'Tickets Sold', value: eventDetails.num_tickets_available - eventDetails.num_tickets_left, fill: '#99c5c4' },
                { name: 'Total tickets available', value: eventDetails.num_tickets_available, fill: '#d3ebeb' },
                { name: 'Historical Attendance', value: trueAttendance, fill: '#99c5c4' }, // Add the historical attendance data here
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => value} /> {/* Display the value as is */}
                <Bar dataKey="value">
                  {
                    // Render different colors for each bar
                    (data) => data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))
                  }
                </Bar>
              </BarChart>

                <p style={{ fontSize: '12px', fontStyle: 'italic', color: 'gray', marginTop: '20px', textAlign: 'center' }}>
                  * Disclaimer: Your privacy is important to us. Any personal information collected during the 
                    use of this website/application will be used solely for the purpose of providing the services and features offered.
                    We may use aggregated, anonymized data for analytical and statistical purposes to improve our services.</p>
              </div>
            </div>
          </div>
        )}
      </React.Fragment>
    </ThemeProvider>
  );
};

export default InsightsPage;