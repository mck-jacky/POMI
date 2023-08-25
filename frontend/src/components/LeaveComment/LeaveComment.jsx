import React, { useState } from 'react'
import { Box } from '@mui/system';
import Avatar from '@mui/material/Avatar';
import Input from '@mui/material/Input';
import Button from '@mui/material/Button';
import { fetchURL } from '../../helper';

const LeaveComment = ({ host, name, token, eventId, threadId, hostId, handleCommentError, setShowCommentError, updateComments }) => {
  const [inputClicked, setInputClicked] = useState(false);
  const [comment, setComment] = useState("");

  const handleCommentChange = (event) => {
    setComment(event.target.value)
  }

  const handleCancelCommentButton = () => {
    setComment("")
    setInputClicked(false)
  }

  async function handleSendCommentButton (event) {
    let API = '';
    let requestData = {}

    if (host) {
      API = "review/reply"
      requestData = {
        thread_id: threadId,
        host_id:  hostId,
        event_id: eventId,
        reply_content: comment
      }
    } else {
      API = "review/post"
      requestData = {
        token: token,
        event_id: eventId,
        review_content: comment
      }
    }

    event.preventDefault();

    const res = await fetchURL(API, 'POST', requestData);
    
    console.log(res)
    if (res.code === 400 || res.code === 500) {
      handleCommentError(res.message.replace(/<\/?p>/g, ''))

      setTimeout(() => {
        setShowCommentError(false);
      }, 2000);
    } else {
      updateComments()
      setComment('')
    }
  }

  return (
    <Box
      sx={{
        marginBottom: 3,
        display: 'flex'
      }}
    >
      <Avatar
        sx={{
          height: 40,
          width: 40,
          bgcolor: 'black',
          marginRight: 2,
        }}
      >
      </Avatar>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          width: "100%"
        }}
      >
        <Input
          fullWidth
          multiline={true}
          onClick={() => setInputClicked(true)}
          onChange={handleCommentChange}
          value={comment}
        />
        {inputClicked && (
          <Box
            sx={{
              display: 'flex',
              marginTop: 2,
              justifyContent: 'flex-end'
            }}
          >
            <Button 
              variant="text"
              onClick={handleCancelCommentButton}
            >
              Cancel
            </Button>
            <Button 
              variant="contained"
              onClick={handleSendCommentButton}
            >
              Send
            </Button>
          </Box>
        )}
      </Box>
    </Box>
  )
}

export default LeaveComment