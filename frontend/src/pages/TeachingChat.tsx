import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Loader2, Send, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
  role: 'assistant' | 'user';
  content: string;
}

const TeachingChat: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId, topic } = location.state || {};
  
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
            // Ask user if they want to continue or evaluate
            const finishMsg: Message = { role: 'assistant', content: data.message };
            setMessages([...newMessages, finishMsg]);
            
            // For now, we auto-redirect to evaluation after a short delay or show a button
            // But per specs: "prompt whether he wants to teach more or evaluate"
            // Let's mock this by showing buttons in the UI instead of text input for the last step
            // For MVP simplicity, let's just show an "Evaluation Ready" state
            
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

  const handleGoToEvaluation = () => {
    navigate('/evaluate', { state: { sessionId } });
  };

  return (
    <Layout>
      <div className="flex flex-col h-[80vh]">
        <div className="text-center mb-4">
            <h2 className="text-xl font-semibold">Teaching: {topic}</h2>
            <p className="text-sm text-muted-foreground">Explain the concepts clearly to your virtual friend.</p>
        </div>

        <Card className="flex-1 flex flex-col overflow-hidden shadow-md border-muted/60">
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                    <div key={idx} className={cn("flex w-full", msg.role === 'user' ? "justify-end" : "justify-start")}>
                        <div className={cn(
                            "flex max-w-[80%] rounded-lg p-3 text-sm",
                            msg.role === 'user' 
                                ? "bg-primary text-primary-foreground" 
                                : "bg-muted text-foreground"
                        )}>
                            {msg.role === 'assistant' && <Bot className="mr-2 h-4 w-4 mt-1 flex-shrink-0" />}
                            {msg.role === 'user' && <User className="mr-2 h-4 w-4 mt-1 flex-shrink-0" />}
                            <div className="leading-relaxed">{msg.content}</div>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start w-full">
                         <div className="flex max-w-[80%] rounded-lg p-3 bg-muted">
                            <Bot className="mr-2 h-4 w-4 mt-1" />
                            <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                    </div>
                )}
                <div ref={scrollRef} />
            </CardContent>
            <CardFooter className="p-4 bg-background border-t">
                {isFinished ? (
                     <div className="w-full flex gap-4">
                        <Button variant="outline" className="w-full" onClick={() => window.location.reload()}>
                            Teach More
                        </Button>
                        <Button className="w-full" onClick={handleGoToEvaluation}>
                            See Evaluation
                        </Button>
                     </div>
                ) : (
                    <div className="flex w-full items-end gap-2">
                        <Textarea 
                            placeholder="Type your explanation..." 
                            className="min-h-[60px]"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                        />
                        <Button size="icon" onClick={handleSend} disabled={!input.trim() || isLoading}>
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                )}
            </CardFooter>
        </Card>
      </div>
    </Layout>
  );
};

export default TeachingChat;
