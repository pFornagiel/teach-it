import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Loader2, CheckCircle, AlertCircle, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EvaluationDetails {
    point: string;
    status: 'correct' | 'partial' | 'wrong';
}

interface EvaluationResult {
    grade: string;
    comments: string;
    details: EvaluationDetails[];
}

const Evaluation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId } = location.state || {};
  const [result, setResult] = useState<EvaluationResult | null>(null);

  useEffect(() => {
    if (!sessionId) {
        navigate('/'); 
        return;
    }

    const fetchEvaluation = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error("Failed to evaluate", error);
        }
    };
    
    fetchEvaluation();
  }, [sessionId, navigate]);

  if (!result) {
    return (
        <Layout>
             <div className="flex flex-col items-center justify-center space-y-4 h-[50vh]">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
                <h2 className="text-xl font-semibold">Grading your performance...</h2>
                <p className="text-muted-foreground animate-pulse">Analyzing your explanations against the source material.</p>
            </div>
        </Layout>
    )
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-500';
    if (grade.startsWith('B')) return 'text-blue-500';
    if (grade.startsWith('C')) return 'text-yellow-500';
    return 'text-red-500';
  }

  return (
    <Layout>
      <div className="space-y-8 animate-in fade-in duration-700">
        <div className="text-center">
            <h2 className="text-3xl font-bold">Session Review</h2>
            <p className="text-muted-foreground">Here is how you did as a teacher.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
             {/* Grade Card */}
             <Card className="col-span-1 border-primary/20 bg-primary/5 flex flex-col items-center justify-center min-h-[200px]">
                <CardHeader>
                    <CardTitle className="text-lg text-muted-foreground">Overall Grade</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className={cn("text-8xl font-black tracking-tighter", getGradeColor(result.grade))}>
                        {result.grade}
                    </div>
                </CardContent>
             </Card>

             {/* Feedback Card */}
             <Card className="col-span-1 md:col-span-2">
                <CardHeader>
                    <CardTitle>Detailed Feedback</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-lg font-medium">{result.comments}</p>
                    <div className="grid gap-2">
                        {result.details.map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 rounded-md bg-muted/50">
                                <span className="font-medium">{item.point}</span>
                                <div className="flex items-center gap-2">
                                    {item.status === 'correct' && <CheckCircle className="h-5 w-5 text-green-500" />}
                                    {item.status === 'partial' && <AlertCircle className="h-5 w-5 text-yellow-500" />}
                                    {item.status === 'wrong' && <AlertCircle className="h-5 w-5 text-red-500" />}
                                    <span className="capitalize text-sm text-muted-foreground">{item.status}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
                <CardFooter>
                    <Button onClick={() => navigate('/')} className="ml-auto">
                        <RotateCcw className="mr-2 h-4 w-4" /> Start New Session
                    </Button>
                </CardFooter>
             </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Evaluation;
