import 'mdb-react-ui-kit/dist/css/mdb.min.css';
import "@fortawesome/fontawesome-free/css/all.min.css";
// eslint-disable-next-line no-unused-vars
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import RegisterPage from './routes/RegisterPage';
import LoginPage from './routes/LoginPage';
import ResetPasswordPage from './routes/ResetPasswordPage';
import EventCreatePage from './routes/EventCreatePage';
import { UserContextProvider } from './userContext';
import EventPage from './routes/EventPage/EventPage';
import MyEventsPage from './routes/MyEventsPage';
import SearchHistoryPage from './routes/SearchHistoryPage';
import MyAccountPage from './routes/MyAccountPage';
import LandingPage from './routes/LandingPage';
import InsightsPage from './routes/EventPage/components/InsightsPage/InsightsPage.jsx';
import MyTicketsPage from './routes/MyTicketsPage';
import AcctInsightsPage from './routes/AcctInsightsPage';


function App() {
  return (
    <div>
      <UserContextProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/reset_password" element={<ResetPasswordPage />} />
            <Route path="/event_create" element={<EventCreatePage />} />
            <Route path="/event/:eventId" element={<EventPage />} />
            <Route path="/my_events" element={<MyEventsPage />} />
            <Route path="/my_account" element={<MyAccountPage />} />
            <Route path="/search_history" element={<SearchHistoryPage />} />
            <Route path="/my_tickets" element={<MyTicketsPage />} />
            <Route path="/event_insights/:eventId" element={<InsightsPage />} />
            <Route path="/users" element={<MyEventsPage />} />
            <Route path="/account_insights" element={<AcctInsightsPage />} />
          </Routes>
        </BrowserRouter>
      </UserContextProvider>
    </div>
  );
}

export default App;
