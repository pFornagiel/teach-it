import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Loader2, Send, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  role: 'assistant' | 'user';
  content: string;
}

const TeachingChat: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId, topic, filename } = location.state || {};
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Initial fetch for the first question
  useEffect(() => {
    if (!sessionId) {
        navigate('/'); // Redirect if no session
        return;
    }

    const startChat = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            const data = await response.json();
            if (data.question) {
                setMessages([{ role: 'assistant', content: data.question }]);
            }
        } catch (error) {
            console.error("Failed to start chat", error);
        } finally {
            setIsLoading(false);
        }
    };
    
    // Only fetch if empty to avoid double fetching on strict mode mounting
    if (messages.length === 0) {
        startChat();
    }
  }, [sessionId, navigate]);

  useEffect(() => {
    if (scrollRef.current) {
        scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input } as Message];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, answer: input })
        });
        const data = await response.json();

        if (data.finished) {
             const finishMsg: Message = { role: 'assistant', content: data.message };
             setMessages([...newMessages, finishMsg]);
        } else {
            setMessages([...newMessages, { role: 'assistant', content: data.question }]);
        }
    } catch (error) {
        console.error("Failed to send message", error);
    } finally {
        setIsLoading(false);
    }
  };

  const isFinished = messages.length > 0 && messages[messages.length - 1].content.includes("Ready for evaluation");

  const [isExiting, setIsExiting] = useState(false);

  const handleGoToEvaluation = () => {
    setIsExiting(true);
    setTimeout(() => {
        navigate('/evaluate', { state: { sessionId, filename } });
    }, 500); // Wait for animation
  };

  const handleTeachMore = async () => {
    try {
        await fetch('http://localhost:5000/api/continue_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        // Fetch next question
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        const data = await response.json();
        
        setMessages(prev => [...prev, { role: 'assistant', content: data.question }]);
        
    } catch (error) {
        console.error("Failed to extend session", error);
    }
  };

  return (
    <Layout>
      <AnimatePresence>
        {!isExiting && (
            <motion.div 
                className="flex flex-col h-[85vh] max-w-3xl mx-auto w-full"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50, transition: { duration: 0.5 } }}
            >
                <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-6"
                >
                    <div className="inline-block p-3 bg-secondary border-2 border-black shadow-neo transform -rotate-2 mb-2">
                        <h2 className="text-xl font-bold uppercase tracking-tight">Topic: {topic}</h2>
                    </div>
                    <p className="text-sm font-medium text-muted-foreground mt-2 bg-white inline-block px-2 py-1 border-2 border-black shadow-neo-sm">TEACH THE AI</p>
                </motion.div>

                <Card className="flex-1 flex flex-col overflow-hidden border-2 border-black shadow-neo bg-white relative">
                    <CardContent className="flex-1 overflow-y-auto p-4 space-y-6">
                        {messages.map((msg, idx) => (
                            <motion.div 
                                key={idx} 
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className={cn("flex w-full", msg.role === 'user' ? "justify-end" : "justify-start")}
                            >
                                <div className={cn(
                                    "flex max-w-[80%] rounded-lg p-4 text-sm font-medium border-2 border-black shadow-neo-sm",
                                    msg.role === 'user' 
                                        ? "bg-primary text-white" 
                                        : "bg-secondary text-black"
                                )}>
                                    {msg.role === 'assistant' && <Bot className="mr-3 h-5 w-5 mt-0.5 flex-shrink-0" />}
                                    {msg.role === 'user' && <User className="mr-3 h-5 w-5 mt-0.5 flex-shrink-0" />}
                                    <div className="leading-relaxed">{msg.content}</div>
                                </div>
                            </motion.div>
                        ))}
                        {isLoading && (
                            <motion.div 
                                initial={{ opacity: 0 }} 
                                animate={{ opacity: 1 }}
                                className="flex justify-start w-full"
                            >
                                <div className="flex max-w-[80%] rounded-lg p-4 bg-muted border-2 border-black shadow-neo-sm">
                                    <Bot className="mr-3 h-5 w-5 mt-0.5" />
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                </div>
                            </motion.div>
                        )}
                        <div ref={scrollRef} />
                    </CardContent>
                    
                    <CardFooter className="p-4 bg-background border-t-2 border-black">
                        <AnimatePresence mode="wait">
                            {isFinished ? (
                                <motion.div 
                                    key="finished-controls"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 20 }}
                                    className="w-full flex gap-4"
                                >
                                    <Button variant="outline" className="w-full bg-white hover:bg-gray-100" onClick={handleTeachMore}>
                                        Teach More
                                    </Button>
                                    <Button className="w-full bg-primary text-white hover:bg-primary/90" onClick={handleGoToEvaluation}>
                                        See Evaluation
                                    </Button>
                                </motion.div>
                            ) : (
                                <motion.div 
                                    key="input-controls"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 20 }}
                                    className="flex w-full items-end gap-2"
                                >
                                    <Textarea 
                                        placeholder="Type your explanation..." 
                                        className="min-h-[60px] resize-none text-base bg-white"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleSend();
                                            }
                                        }}
                                    />
                                    <Button size="icon" onClick={handleSend} disabled={!input.trim() || isLoading} className="h-[60px] w-[60px]">
                                        <Send className="h-6 w-6" />
                                    </Button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </CardFooter>
                </Card>
            </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
};

export default TeachingChat;
