import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Loader2, Plus } from 'lucide-react';
import { Input } from '@/components/ui/input';

const TopicSelection: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [topics, setTopics] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [customTopic, setCustomTopic] = useState('');

  useEffect(() => {
    // In a real app, we might pass the filename to get specific topics
    // const filename = location.state?.filename; 
    
    const fetchTopics = async () => {
      const filename = location.state?.filename;
      if (!filename) return;

      try {
        const response = await fetch('http://localhost:5000/api/topics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
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
  }, []);

  const handleSelectTopic = async (topic: string) => {
    // Get filename from location state as well, or prompt user if missing (though it should be there)
    const filename = location.state?.filename; 

    try {
        const response = await fetch('http://localhost:5000/api/start_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, filename })
        });
        const data = await response.json();
        navigate('/chat', { state: { sessionId: data.session_id, topic } });
    } catch (error) {
        console.error("Failed to start session", error);
    }
  };

  const handleAddCustomTopic = () => {
    if (customTopic.trim()) {
        handleSelectTopic(customTopic);
    }
  };

  if (loading) {
    return (
        <Layout>
            <div className="flex flex-col items-center justify-center space-y-4 h-[50vh]">
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
                <p className="text-muted-foreground animate-pulse">Analyzing your notes...</p>
            </div>
        </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">What would you like to learn today?</h2>
            <p className="text-muted-foreground">Select a topic generated from your notes, or add your own.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {topics.map((topic, index) => (
                <Card key={index} className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => handleSelectTopic(topic)}>
                    <CardHeader>
                        <CardTitle className="text-lg">{topic}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">Click to start teaching this topic.</p>
                    </CardContent>
                </Card>
            ))}
             <Card className="border-dashed">
                <CardHeader>
                    <CardTitle className="text-lg">Custom Topic</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                    <Input 
                        placeholder="e.g. Advanced Calculus" 
                        value={customTopic}
                        onChange={(e) => setCustomTopic(e.target.value)}
                    />
                </CardContent>
                <CardFooter>
                    <Button variant="outline" className="w-full" onClick={handleAddCustomTopic} disabled={!customTopic.trim()}>
                        <Plus className="mr-2 h-4 w-4" /> Add & Start
                    </Button>
                </CardFooter>
            </Card>
        </div>
      </div>
    </Layout>
  );
};

export default TopicSelection;
