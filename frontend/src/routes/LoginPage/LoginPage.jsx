import React, { useContext, useState } from 'react';
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
import image1 from '../../images/Login1.gif'

const LoginPage = () => {
  const [show, setShow] = useState(false)
  const [errorMessage, setErrorMessage] = useState('Error')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const navigate = useNavigate();
  const userObj = useContext(UserContext);

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  async function handleSubmit (event) {
    event.preventDefault();

    const res = await fetchURL('auth/login', 'POST', {
      email,
      password
    })

    console.log(res)

    if (res.code === 400) {
      // show error message
      setShow(true)
      setErrorMessage(res.message.replace(/<\/?p>/g, ''))
    } else if (res.code !== 400 && res.code !== 500) {
      setShow(false)
      userObj.setUser({
        token: res.token,
        email
      });
      localStorage.token = res.token;
      localStorage.email = email;
      navigate('/');
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
              Sign in
              </h1>

              <Box component="form" onSubmit={handleSubmit}>
                <MDBInput wrapperClass='mb-4' label='Email' id='email' name="email" type='email' onChange={handleEmailChange}/>
                <MDBInput wrapperClass='mb-4' label='Password' id='password' name="password" type='password' onChange={handlePasswordChange}/>

                <MDBBtn style={{backgroundColor: "#99c5c4"}} className='w-100 mb-4' size='md'>sign in</MDBBtn>
              </Box>

              <div className="text-center">

                <p>New here? Register <Link to="/register">here</Link></p>
                <p>Forgot password? Click <Link to="/reset_password">here</Link></p>

              </div>

            </MDBCardBody>
          </div>
        </MDBCol>

      </MDBRow>

    </MDBContainer>
  );
}

export default LoginPage