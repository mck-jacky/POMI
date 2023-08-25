import React from 'react'
import { Box } from '@mui/system';

const MyAccountBox = ({ children }) => {
  return (
    <Box
      sx={{
        boxShadow: "0px 6px 16px rgba(0, 0, 0, 0.12)",
        minHeight: "156px",
        padding: "16px",
        borderRadius: "12px",
        marginRight: "13px",
        marginBottom: "13px",
        width: "340px",
        maxHeight: "168px",
        height: "168px"
      }}
    >
      {children}
    </Box>
  )
}

export default MyAccountBox