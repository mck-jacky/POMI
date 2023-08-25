import React, { useState, useEffect } from 'react';
import { fetchGetURL } from '../../helper';
import NavBar from '../../components/NavBar';
import TableContainer from '@mui/material/TableContainer';
import { Box, Paper } from '@mui/material';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableBody from '@mui/material/TableBody';
import './SearchHistoryPage.css';

const SearchHistoryPage = () => {
  const [searchHistory, setSearchHistory] = useState([]);

  useEffect(() => {
    const fetchSearchHistory = async () => {
      try {
        const res = await fetchGetURL('search/history', {
          token: localStorage.token, // Pass the user's token as a parameter
        });
        console.log(res)
        setSearchHistory(res); // Update the search history state with the entire array
      } catch (error) {
        console.error(error);
      }
    };
  
    fetchSearchHistory();
  }, []);
  
  return (
    <div>
      <div className="ocean">
        <div className="wave"></div>
        <div className="wave"></div>
      </div>
      <NavBar />
      <Box sx={{ marginTop: '20px' }}>
        <div className="page-title">
          <div className="waviy">
            <span style={{'--i': 1}}>S</span>
            <span style={{'--i': 2}}>E</span>
            <span style={{'--i': 3}}>A</span>
            <span style={{'--i': 4}}>R</span>
            <span style={{'--i': 5}}>C</span>
            <span style={{'--i': 6}}>H</span>
            <span style={{'--i': 7}}>&nbsp;</span>
            <span style={{'--i': 8}}>H</span>
            <span style={{'--i': 9}}>I</span>
            <span style={{'--i': 10}}>S</span>
            <span style={{'--i': 11}}>T</span>
            <span style={{'--i': 12}}>O</span>
            <span style={{'--i': 13}}>R</span>
            <span style={{'--i': 14}}>Y</span>
          </div>
        </div>
      </Box>
      <div className="search-history-page" style={{ maxHeight: '400px', overflow: 'auto', position: 'relative', zIndex: 1 }}>
      <Paper elevation={1} sx={{ width: '80%', marginTop: '20px' }}>
      <TableContainer component={Paper}>
        <Table sx={{ backgroundColor: '#fbfbfb', borderRadius: '20px' }}>
          <TableHead>
            <TableRow>
              <TableCell style={{ textAlign: 'center', fontWeight: 'bold', borderBottom: '1px solid black' }}>
                Search Query
              </TableCell>
              <TableCell style={{ textAlign: 'center', fontWeight: 'bold', borderBottom: '1px solid black' }}>
                Date
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {searchHistory.map((query, index) => (
              <TableRow key={index}>
                <TableCell style={{ textAlign: 'center' }}>{query}</TableCell>
                <TableCell style={{ textAlign: 'center' }}>{new Date().toLocaleDateString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      </Paper>
      </div>
    </div>
  );
};

export default SearchHistoryPage;