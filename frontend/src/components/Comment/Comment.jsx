import React from 'react'
import Avatar from '@mui/material/Avatar';
import { Box } from '@mui/system';
import Typography from '@mui/material/Typography';

const Comment = ({ host, name, comment }) => {
  const marginLeft = host ? 6 : 0;
  const size = host ? 34 : 40;

  return (
    <Box
      sx={{
        display: 'flex',
        marginBottom: 2,
        marginLeft: marginLeft
      }}
    >
      <Avatar
        sx={{
          height: size,
          width: size,
          bgcolor: 'black'
        }}
      >
        {name[0]}
      </Avatar>
      <Box
        sx={{
          marginLeft: 2
        }}
      >
        <Typography 
          sx={{
            color: '#1e0a3c',
          }}  
          >
          <b>{name}</b>
        </Typography>
        <Typography>
          {comment}
        </Typography>
      </Box>
    </Box>
  )
}

export default Comment