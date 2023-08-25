import React, { useState } from 'react'
import {
  MDBBtn,
  MDBContainer,
  MDBRow,
  MDBCol,
  MDBCardBody,
  MDBInput,
}
from 'mdb-react-ui-kit';
import Box from '@mui/material/Box';
import { Link } from 'react-router-dom';
import { fetchURL } from '../../helper'; 
import Alert from '@mui/material/Alert';
import image1 from '../../images/Login1.gif'

const ResetPasswordPage = () => {
  const [step, setStep] = useState(1)
  const [show, setShow] = useState(false)
  const [errorMessage, setErrorMessage] = useState('Error')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [password, setPassword] = useState('')

  const setShowErrorMessage = (message) => {
    setShow(true)
    setErrorMessage(message.replace(/<\/?p>/g, ''))
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  const handleEmailChange = (event) => {
    setEmail(event.target.value)
  }

  const handleCodeChange = (event) => {
    setCode(event.target.value)
  }

  const handlePasswordChange = (event) => {
    setPassword(event.target.value)
  }

  async function handleEmailNextClick (event) {
    event.preventDefault();

    if (email === "") {
      setShowErrorMessage("Please enter your email")
      return
    } else {

      const res = await fetchURL('auth/password/reset/request', 'POST', {
        email: email
      })

      if (res.code === 400 || res.code === 500) {
        setShow(true)
        setErrorMessage(res.message.replace(/<\/?p>/g, ''))
      } else {
        setStep(step+1);
        setShow(false)
      }
    }
  }

  async function handleCodeClick (event) {
    event.preventDefault();

    if (code === "") {
      setShowErrorMessage("Please enter your verification code")
      return
    } else {

      const res = await fetchURL('auth/password/reset/verify', 'POST', {
        code: code
      })

      if (res.code === 400 || res.code === 500) {
        setShow(true)
        setErrorMessage("Incorrect verification code.")
      } else {
        setStep(step+1);
        setShow(false)
      }
    }
  }

  async function handleNewPasswordClick (event) {
    event.preventDefault();

    if (password === "") {
      setShowErrorMessage("Please enter your new password")
      return
    } else {
      
      const res = await fetchURL('auth/password/reset/reset', 'POST', {
        code: code,
        password: password
      })

      if (res.code === 400) {
        setShow(true)
        setErrorMessage(res.message)
      } else {
        setStep(step+1);
        setShow(false)
      }
    }
  }

  return (
    <MDBContainer fluid style={{margin: 0, padding: 0}}>

      {show &&
        <Alert severity='error' onClose={() => setShow(false)}>{errorMessage}</Alert>
      }

      <MDBRow style={{height: '100vh'}}>

        <MDBCol md='6' className='text-center text-md-start d-flex flex-column justify-content-center'>

          <img src={image1} className="w-100 rounded-4 shadow-4"
              alt="" fluid/>

        </MDBCol>

        <MDBCol md='6' className='text-center text-md-start d-flex flex-column justify-content-center'>

          <div>
            <MDBCardBody className='p-5'>

              <Link to="/" style={{ color: 'inherit', textDecoration: 'inherit' }}>
                <h3 className="ls-tight" style={{color: "#99c5c4"}}>
                  POMI
                </h3>
              </Link>

              <h1 className="my-3 display-5 fw-bold ls-tight">
                Reset your password
              </h1>

              {step === 1 && (
                <h3 className="my-3 ls-tight">
                  Enter your email
                </h3>
              )}

              {step === 2 && (
                <h3 className="my-3 ls-tight">
                  We sent an email to <b>{email}</b>! Please find the verification code in this email to reset your password.
                </h3>
              )}

              {step === 3 && (
                <h3 className="my-3 ls-tight">
                  Enter your new password
                </h3>
              )}
              
              <Box>
                {step === 1 && (
                  <>
                    <MDBInput wrapperClass='mb-4' label='Email' id='email' name="email" type='email' onChange={handleEmailChange}/>
                    <MDBBtn style={{backgroundColor: "#99c5c4"}} className='w-100 mb-4' size='md' onClick={handleEmailNextClick}>Continue</MDBBtn>
                  </>
                )}
                {step === 2 && (
                  <>
                    <MDBInput wrapperClass='mb-4' label='Verification code' id='' name="" type='' onChange={handleCodeChange}/>
                    <MDBBtn style={{backgroundColor: "#99c5c4"}} className='w-100 mb-4' size='md' onClick={handleCodeClick}>Continue</MDBBtn>
                  </>
                )}
                {step === 3 && (
                  <>
                    <MDBInput wrapperClass='mb-4' label='New password' id='' name="" type='' onChange={handlePasswordChange}/>
                    <MDBBtn style={{backgroundColor: "#99c5c4"}} className='w-100 mb-4' size='md' onClick={handleNewPasswordClick}>Continue</MDBBtn>
                  </>
                )}
              </Box>

              {step === 4 && (
                <h3 className="my-3 ls-tight">
                  Reset successfully. Login <Link to="/login">here</Link>
                </h3>
              )}

            </MDBCardBody>
          </div>
        </MDBCol>

      </MDBRow>

    </MDBContainer>
  );
}

export default ResetPasswordPage