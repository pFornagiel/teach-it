import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Welcome from '@/pages/Welcome';
import TopicSelection from '@/pages/TopicSelection';
import TeachingChat from '@/pages/TeachingChat';
import Evaluation from '@/pages/Evaluation';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/topics" element={<TopicSelection />} />
        <Route path="/chat" element={<TeachingChat />} />
        <Route path="/evaluate" element={<Evaluation />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
