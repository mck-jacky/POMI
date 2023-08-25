import React, { useState, useContext } from 'react'
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
import { Link, useNavigate } from 'react-router-dom';
import { fetchURL } from '../../helper'; 
import Alert from '@mui/material/Alert';
import { UserContext } from '../../userContext';
import ArrowBackIosNewOutlinedIcon from '@mui/icons-material/ArrowBackIosNewOutlined';
import image1 from '../../images/Register1.gif'

const RegisterPage = () => {
  const [step, setStep] = useState(1)
  const [show, setShow] = useState(false)
  const [errorMessage, setErrorMessage] = useState('Error')

  const [fname, setFname] = useState('')
  const [lname, setLname] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [creditCardName, setCreditCardName] = useState('')
  const [creditCardNumber, setCreditCardNumber] = useState('')
  const [creditCardExpiration, setCreditCardExpiration] = useState('')
  const [creditCardCVV, setCreditCardCVV] = useState('')

  const userObj = useContext(UserContext);
  const navigate = useNavigate();

  async function handleNextClick (event) {
    event.preventDefault();

    const res = await fetchURL('auth/register', 'POST', {
      input_email: email,
      password: password,
      first_name: fname,
      last_name: lname,
      cardholder_name: creditCardName,
      card_number: creditCardNumber,
      expiry_month: creditCardExpiration.split("/")[0],
      expiry_year: "20"+creditCardExpiration.split("/")[1],
      cvv_num: creditCardCVV
    })

    if (res.message.replace(/<\/?p>/g, '') === "Sorry, the email you entered is not valid." ||
        res.message.replace(/<\/?p>/g, '') === "Email is taken! Please enter another email." || 
        res.message.replace(/<\/?p>/g, '') === "First name should be between 1 and 50 characters" ||
        res.message.replace(/<\/?p>/g, '') === "Last name should be between 1 and 50 characters" ||
        res.message.replace(/<\/?p>/g, '') === "Password is too short: password must not be less than 6 characters"
    ) {
      setShow(true)
      setErrorMessage(res.message.replace(/<\/?p>/g, ''))
    } else {
      setShow(false)
      setStep(2);

    } 
  }

  const handleBackClick = () => {
    setStep(1)
  }

  const handleFnameChange = (event) => {
    setFname(event.target.value)
  }

  const handleLnameChange = (event) => {
    setLname(event.target.value)
  }

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleCreditCardNameChange = (e) => {
    setCreditCardName(e.target.value);
  };

  const handleCreditCardNumberChange = (e) => {
    const input = e.target.value.replace(/\D/g, ''); // Remove non-digit characters
    setCreditCardNumber(input);
  };

  const handleCreditCardExpirationChange = (e) => {
    const input = e.target.value.replace(/\D/g, ''); // Remove non-digit characters
    let formattedInput = input.slice(0, 4);
    formattedInput = formatExpirationInput(formattedInput);
    setCreditCardExpiration(formattedInput);

  };

  const handleCreditCardCVV = (e) => {
    const input = e.target.value.replace(/\D/g, ''); // Remove non-digit characters
    const formattedInput = input.slice(0, 3);
    setCreditCardCVV(formattedInput);
  };

  const formatExpirationInput = (input) => {
    let formattedInput = input.replace(/\D/g, ''); // Remove non-digit characters
    if (formattedInput.length > 2) {
      formattedInput = formattedInput.slice(0, 2) + '/' + formattedInput.slice(2);
    }
    return formattedInput;
  };

  async function handleSubmit (event) {
    event.preventDefault();

    const res = await fetchURL('auth/register', 'POST', {
      input_email: email,
      password: password,
      first_name: fname,
      last_name: lname,
      cardholder_name: creditCardName,
      card_number: creditCardNumber,
      expiry_month: creditCardExpiration.split("/")[0],
      expiry_year: "20"+creditCardExpiration.split("/")[1],
      cvv_num: creditCardCVV
    })

    console.log(res)
    console.log(res.code)
    
    if (res.code === 400) {
      setShow(true)
      setErrorMessage(res.message.replace(/<\/?p>/g, ''))
    } else if (res.code !== 400 && res.code !== 500) {
      setShow(false)
      userObj.setUser({
        token: res.token,
        email
      })
      localStorage.token = res.token
      localStorage.email = email
      console.log(userObj)
      navigate('/');
    }
  }

  return (
    <MDBContainer fluid="true" style={{margin: 0, padding: 0}}>
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

              {step === 1 && (
                <h1 className="my-3 display-5 fw-bold ls-tight">
                  Create an account
                </h1>
              )}

              {step === 2 && (
                <h1 className="my-3 display-5 fw-bold ls-tight">
                  <ArrowBackIosNewOutlinedIcon
                    sx={{
                      fontSize: '2rem', // Adjust the font size to make the icon bigger
                      marginRight: '0.5rem', // Adjust the margin right as needed
                      cursor: 'pointer'
                    }}
                    onClick={handleBackClick}
                  />
                  Payment information
                </h1>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                {/* EMAIL AND PASSWORD */}
                {step === 1 && (
                  <>
                    <MDBInput wrapperClass='mb-4' label='First Name' id='register-fname' name="fname" type='text' value={fname} onChange={handleFnameChange}/>
                    <MDBInput wrapperClass='mb-4' label='Last Name' id='register-lname' name="lname" type='text' value={lname} onChange={handleLnameChange}/>
                    <MDBInput wrapperClass='mb-4' label='Email' id='register-email' name="email" type='email' value={email} onChange={handleEmailChange}/>
                    <MDBInput wrapperClass='mb-4' label='Password' id='register-password' name="password" type='password' value={password} onChange={handlePasswordChange}/>
                    <MDBBtn style={{backgroundColor: "#99c5c4"}} className='w-100 mb-4' size='md' onClick={handleNextClick}>sign up</MDBBtn>
                  </>
                )}
                {/* PAYMENT DETAILS */}
                {step === 2 && (
                  <>
                    <MDBInput wrapperClass="mb-4" label="Name" id="name" name="name" type="text" value={creditCardName} onChange={handleCreditCardNameChange}/>
                    <MDBInput wrapperClass="mb-4" label="Card Number" id="cardNumber" name="cardNumber" type="text" value={creditCardNumber} onChange={handleCreditCardNumberChange}/>
                    <div className="row">
                      <div className="col-md-6">
                        <MDBInput wrapperClass="mb-4" label="Expiration (mm/yy)" id="expiration" name="expiration" type="text" value={creditCardExpiration} onChange={handleCreditCardExpirationChange}/>
                      </div>
                      <div className="col-md-6">
                        <MDBInput wrapperClass="mb-4" label="Security Code" id="securityCode" name="securityCode" type="text" value={creditCardCVV} onChange={handleCreditCardCVV}/>
                      </div>
                    </div>
                    <MDBBtn style={{backgroundColor: "#99c5c4"}} className='w-100 mb-4' size='md' type='submit'>sign up</MDBBtn>
                  </>
                )}
              </Box>

              <div className="text-center">

              <p>Already have an account? Login <Link to="/login">here</Link></p>

              </div>

            </MDBCardBody>
          </div>
        </MDBCol>

      </MDBRow>

    </MDBContainer>
  );
}

export default RegisterPage

