import React, { useContext, useState, useEffect } from 'react';
import { fetchGetURL } from '../../helper';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Autocomplete from '@mui/material/Autocomplete';
import { UserContext } from '../../userContext';
import { Link } from 'react-router-dom';

const SearchFunction = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchQueryType, setSearchQueryType] = useState('');
  const [category, setCategory] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [dictionary, setDictionary] = useState([]);

  useEffect(() => {
    fetchDictionary();
  }, []);

  const fetchDictionary = async () => {
    try {
      const res = await fetchGetURL('event/list/get');
      const events = res.map((event) => ({
        event_id: event.event_id,
        event_title: event.event_title,
        event_description: event.event_description,
        full_text: `${event.event_title} ${event.event_description}`,
      }));
      setDictionary(events);
    } catch (error) {
      console.error(error);
    }
  };
  const handleSearch = async () => {
    try {
      const res = await fetchGetURL('event/search', {
        token: localStorage.token,
        event_keyword: searchQuery,
        event_type: searchQueryType,
        
      });
      console.log(res);
      setSearchResults(res);
      setShowResults(true);
    } catch (error) {
      console.error(error);
      const res = await fetchGetURL('event/search', {
        token: '',
        event_keyword: searchQuery,
        event_type: searchQueryType,
    });
  }};

  const handleInputChange = (event, value) => {
    setSearchQuery(value);
  
    // Filter the dictionary for suggestions that contain the user's input in title or description
    const filteredSuggestions = dictionary.filter(
      (event) =>
        event.full_text.toLowerCase().includes(value.toLowerCase())
    );
    setSuggestions(filteredSuggestions);
  };
  
  const handleCategoryChange = (event) => {
    const selectedType = event.target.value;
    setSearchQueryType(selectedType);
    setCategory(selectedType);
  };

  const handleSearchClick = () => {
    handleSearch(); // Trigger search when the "Search" button is clicked
  };

  const handleClose = () => {
    setShowResults(false);
  };

  const getOptionLabel = (option) => {
    if (!option || !option.event_title) {
      return ""; // Return an empty string if option is undefined or has no event_title
    }
    return option.event_title;
  };

  return (
    <div>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Autocomplete
          value={suggestions.find((option) => option.event_title === searchQuery) || null}
          options={suggestions}
          getOptionLabel={getOptionLabel}
          onInputChange={handleInputChange}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Search by Event Keyword..."
              variant="outlined"
              size="small"
              style={{ width: '200px' }}
            />
          )}
          clearOnBlur={false} // Set clearOnBlur to false
          popupIcon={null}
        />
        <FormControl>
          <InputLabel
            htmlFor="category-select"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '55%',
              paddingBottom: '10px',
            }}
          >
            Category
          </InputLabel>
          <Select
            value={category}
            labelId="category-select"
            label="Category"
            onChange={handleCategoryChange}
            size="small"
            style={{ width: '200px' }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value={'Music'}>Music</MenuItem>
            <MenuItem value={'Performing & Visual Arts'}>
              Performing & Visual Arts
            </MenuItem>
            <MenuItem value={'Seasonal'}>Seasonal</MenuItem>
            <MenuItem value={'Health'}>Health</MenuItem>
            <MenuItem value={'Hobbies'}>Hobbies</MenuItem>
            <MenuItem value={'Business'}>Business</MenuItem>
            <MenuItem value={'Food & Drink'}>Food & Drink</MenuItem>
            <MenuItem value={'Sports & Fitness'}>Sports & Fitness</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" onClick={handleSearchClick}>
          Search
        </Button>
      </Box>

      <Dialog
        open={showResults}
        onClose={handleClose}
        PaperProps={{ sx: { minWidth: '500px' } }}
      >
        <DialogTitle style={{ textAlign: 'center', fontWeight: 'bold' }}>Search Results</DialogTitle>
        <DialogContent>
          {searchResults.map((event) => (
            <Link to={`/event/${event.event_id}`} key={event.event_id}>
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center', // Center the events horizontally
                  padding: '10px',
                  border: '1px solid #ccc',
                  borderRadius: '5px',
                  marginBottom: '10px',
                }}
              >
                <h3 style={{ color: '#99c5c4' }}>{event.event_title}</h3>
                <p style={{ color: '#000000' }}>Description: {event.event_description}</p>
                <p style={{ color: '#000000' }}>Event Type: {event.event_type}</p>
              </div>
            </Link>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default SearchFunction;