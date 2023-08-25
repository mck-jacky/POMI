import React from 'react'
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import { formatTimeString } from '../../helper';

const EventCard2 = ({ title, start_date_time, venue, image, type, id }) => {
  if (image === '') {
    image =
      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARMAAAC3CAMAAAAGjUrGAAAAM1BMVEXp7vG6vsHs8fS3u77Fycy+wsXc4eTX3N/h5unT2NrHzM7N0tW1ubzu8/W7v8LBxcjl6uwx8f6JAAADy0lEQVR4nO2c23aDIBBFCQheUf//a6vRpEZuJgXj0LNXH7oaK3WXwXEQGAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwGnw9Hz7Et+Ds1ElpxoJaeGsHHqRHlkoKlJ0JbvbKQhRjCSs8FKcY+RuRVKQwqsTlUxShm9f8BGGU53cuvryHeXUyLnTj9++5hC8WJ2kv+2sTkR79Y4y9uuf2papKVYnxcWd8GpV0uj0aaxcnFx9lH04ESeMfLpZ2pLJW/obZzrhcGK2BSdmW3BitkXdyfxYz7mO2hZtJ7yqCznIoVUsXv8h7YSPzZJ2CtENZTQplJ1Mj0CbZ6CuiFUdI+yEt69PhUJGih+6Tni5L7qJJlJbZJ2MZu1A1FHuP2Sd7CPnTh+nLapOKtNIrIyOqhNe28puYvjXThp7KfKAE16FDqDqxF6x7sI1VK26wFCcmRMR6gOTEhG6P+XmJNRPtJrruqL0SSHrxD6ehJxwtZS6vVLIOrFP9wTuO1o95XnCh6qTj/ITrsSRQ8k6Ydbg8YYOV9tDhbO4QNaJbUrd301elXikkHUyZbLGc7F34m4bOI9z2ccUuk6Ybl+liMFXP9GGEme/IuxkfubZXKcofL+vVW8ocYUPZSfThRbdYkUIWftKj3YljjyFtBPGtWplL259UzJfZmoLHPeYQtvJMr0zjsxfnnYrsY4p1J0c+l1H4DzOaByfv5N9XhLsKfk7MfOSkJTsnYSVGANt7k50IHBsZ83ciSsv8faUjJxw821w303YLSUfJ7q+VbvPjit5eRs2Gyfzw0//usTkaODsz5yLk6mXTPTbnhLKS5xSMnGyKJnnMn4j4I3AWeie9e8cnGxmSh/h876S55CShZNtEX8Nn3eG1xyd6Nf59FnKsVQtXyf7qR5R6U96SU5OLG9dVB8pyceJbUJQvpOX5OdElx9dfs5OdMxVgnk4ibtwMgsnvI5oJA8nMceSTJxEHUvycBJ/ETZ5JwnWpZN3Yn1n+H874RJODr4LCidwAic74MQETkzgxAROTODEBE5MzDy2i763VEfcCVOlmr+UMr8J/8DxybpIjKyTlG3BidkWnJhtwYnZFpyYbcGJ2VZBwwkb18SqV6lb4usUyeX3NmTrJozzvy81j7S2Sd8l/4a27XeSFHH5jbqfG4OexvVDx7HjSTqu300Y+91p+BS6NuregKnQjn1gEiBCe6RcBl7K6AUCO0VFRMm89EK1RXKatoq4e+QJJN+N+r4jNQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzuIHpk8/wVCHmdcAAAAASUVORK5CYII=';
  }

  start_date_time = formatTimeString(start_date_time)

  const navigate = useNavigate();
  
  return (
    <Box
      sx={{
        minHeight: "340px",
        maxHeight: "34px",
        borderRadius: "12px",
        marginRight: "13px",
        width: "355px",
        transition: "box-shadow 0.3s", // Add transition for smooth effect
        "&:hover": {
          boxShadow: "0px 6px 16px rgba(0, 0, 0, 0.12)", // Apply box shadow on hover
          cursor: "pointer"
        },
      }}
      onClick={() => navigate('/event/' + id)}
    >
      <Box
        sx={{
          position: "relative",
          borderRadius: "5px",
          width: "100%",
          maxHeight: "220px"
        }}
      >
        <Box
          sx={{
            minHeight: "220px"
          }}
        >
          <Box
            component="img"
            sx={{
              objectFit: "cover",
              borderRadius: "5px",
              width: "100%",
              maxHeight: "220px",
            }}
            alt="event-image"
            src={image}
          />
        </Box>

        <Box
          sx={{
            position: "absolute",
            top: "10px",
            left: "10px",
            padding: "4px 8px",
            backgroundColor: "rgba(0, 0, 0, 0.7)",
            color: "white",
            borderRadius: "4px",
            fontSize: "12px",
            fontWeight: "bold"
          }}
        >
          {type}
        </Box>
      </Box>

      <Box
        sx={{
          padding: "2px"
        }}
      >
      <Typography
        sx={{
          marginTop: 1,
          marginBottom: 1,
          fontSize: "16px",
          lineHeight: "20px",
          color: "#99c5c4",
          fontWeight: 600,
          width: "100%",
          textTransform: "uppercase"
        }}
      >
        {start_date_time}
      </Typography>

      <Typography
        sx={{
          marginTop:1,
          marginBottom: 1,
          fontSize: "16px",
          lineHeight: "20px",
          color: "#222222",
          fontWeight: 800,
          width: "100%"
        }}
      >
        {title}
      </Typography>

      <Typography
        sx={{
          marginTop:1,
          marginBottom: 1,
          fontSize: "16px",
          lineHeight: "20px",
          color: "grey",
          fontWeight: 500,
          width: "100%"
        }}
      >
        {venue}
      </Typography>
      </Box>

    </Box>
  )
}

export default EventCard2