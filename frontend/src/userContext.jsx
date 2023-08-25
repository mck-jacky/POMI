import React from 'react';

export const UserContext = React.createContext();

export const UserContextProvider = ({ children }) => {
  const [user, setUser] = React.useState(() => {
    if (localStorage.token && localStorage.email) {
      return {
        token: localStorage.token,
        email: localStorage.email
      }
    } else {
      return {}
    }
  });

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}