import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, Plus, ArrowRight, BookOpen, Eye } from 'lucide-react';
import { motion } from 'framer-motion';

const TopicSelection: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [topics, setTopics] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [customTopic, setCustomTopic] = useState('');

  useEffect(() => {
    // In a real app, we might pass the filename to get specific topics
    const fetchTopics = async () => {
      const filenames = location.state?.filenames;
      const filename = location.state?.filename; // Fallback
      
      const payload = filenames ? { filenames } : { filename };
      
      if (!filenames && !filename) return;

      try {
        const response = await fetch('http://localhost:5000/api/topics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        setTopics(data.topics);
      } catch (error) {
        console.error('Failed to fetch topics', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTopics();
  }, [location.state?.filename]);

  const handleSelectTopic = async (topic: string) => {
    const filename = location.state?.filename;

    try {
      const response = await fetch('http://localhost:5000/api/start_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, filename })
      });
      const data = await response.json();
      navigate('/chat', { state: { sessionId: data.session_id, topic, filename } });
    const filenames = location.state?.filenames; 

    try {
        const response = await fetch('http://localhost:5000/api/start_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, filenames })
        });
        const data = await response.json();
        navigate('/chat', { state: { sessionId: data.session_id, topic, filenames } });
    } catch (error) {
      console.error("Failed to start session", error);
    }
  };

  const handleViewNotes = () => {
    navigate('/notes', { state: { filename: location.state?.filename } });
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center space-y-6 h-[60vh]">
          <div className="w-24 h-24 bg-secondary rounded-full border-4 border-black flex items-center justify-center animate-bounce shadow-neo">
            <Loader2 className="h-12 w-12 animate-spin text-black" />
          </div>
          <h2 className="text-3xl font-display font-bold">Analyzing Knowledge Base...</h2>
          <div className="w-64 h-4 bg-gray-200 rounded-full border-2 border-black overflow-hidden relative">
            <motion.div
              className="h-full bg-primary"
              initial={{ width: "0%" }}
              animate={{ width: "95%" }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
            />
          </div>
        </div>
      </Layout>
    )
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <Layout>
      <motion.div
        className="space-y-8 w-full max-w-4xl"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="text-center space-y-2">
          <motion.div variants={itemVariants} className="inline-block bg-neo-green px-4 py-1 border-2 border-black shadow-neo-sm transform -rotate-1 mb-4">
            <span className="font-bold font-mono text-sm uppercase">Step 2: Selection</span>
          </motion.div>
          <motion.h2 variants={itemVariants} className="text-4xl md:text-5xl font-display font-black tracking-tight uppercase leading-none">
            What will you teach?
          </motion.h2>
          <motion.p variants={itemVariants} className="text-xl text-muted-foreground font-medium max-w-2xl mx-auto">
            Select a topic extracted from your notes, or propose your own syllabus.
          </motion.p>
        </div>

        <motion.div variants={itemVariants} className="flex justify-center">
          <Button
            onClick={handleViewNotes}
            variant="outline"
            className="border-2 border-black shadow-neo-sm hover:shadow-neo transition-all bg-white"
          >
            <Eye className="w-4 h-4 mr-2" />
            View Notes
          </Button>
        </motion.div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {topics.map((topic, index) => (
            <motion.div variants={itemVariants} key={index} whileHover={{ y: -5, transition: { duration: 0.2 } }}>
              <Card
                className="h-full cursor-pointer hover:border-black hover:shadow-neo-lg transition-all duration-300 border-2 border-black shadow-neo bg-white group relative overflow-hidden"
                onClick={() => handleSelectTopic(topic)}
              >
                <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                  <BookOpen className="w-24 h-24" />
                </div>
                <CardContent className="p-6 flex flex-col justify-between h-full relative z-10">
                  <h3 className="font-bold text-xl mb-4 font-display leading-tight">{topic}</h3>
                  <div className="flex justify-end">
                    <div className="w-8 h-8 rounded-full bg-accent border-2 border-black flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}

          <motion.div variants={itemVariants}>
            <Card className="h-full border-2 border-dashed border-gray-400 bg-transparent flex flex-col items-center justify-center p-6 space-y-4 hover:border-black hover:bg-white hover:shadow-neo transition-all duration-300">
              <div className="w-12 h-12 rounded-full bg-secondary border-2 border-black flex items-center justify-center">
                <Plus className="w-6 h-6" />
              </div>
              <div className="w-full space-y-2">
                <p className="font-bold text-center">Custom Topic</p>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter topic..."
                    value={customTopic}
                    onChange={(e) => setCustomTopic(e.target.value)}
                    className="bg-white"
                  />
                  <Button size="icon" onClick={() => { if (customTopic) handleSelectTopic(customTopic) }} className="shrink-0">
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </motion.div>
    </Layout>
  );
};

export default TopicSelection;
