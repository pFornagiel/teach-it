import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Loader2, CheckCircle, AlertCircle, RotateCcw, PartyPopper } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

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
  const { sessionId, filename } = location.state || {};
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0, scale: 0.9 },
    visible: { y: 0, opacity: 1, scale: 1 }
  };

  if (!result) {
    return (
        <Layout>
             <div className="flex flex-col items-center justify-center space-y-6 h-[60vh]">
                <div className="w-24 h-24 bg-secondary rounded-full border-4 border-black flex items-center justify-center animate-bounce shadow-neo">
                    <Loader2 className="h-12 w-12 animate-spin text-black" />
                </div>
                <h2 className="text-3xl font-display font-bold">Grading in progress...</h2>
                <div className="w-64 h-4 bg-gray-200 rounded-full border-2 border-black overflow-hidden relative">
                    <motion.div 
                        className="h-full bg-primary"
                        initial={{ width: "0%" }}
                        animate={{ width: "95%" }}
                        transition={{ duration: 2, ease: "easeInOut" }}
                    />
                </div>
            </div>
        </Layout>
    )
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'bg-neo-green text-black';
    if (grade.startsWith('B')) return 'bg-neo-blue text-black';
    if (grade.startsWith('C')) return 'bg-secondary text-black';
    return 'bg-destructive text-white';
  }

  return (
    <Layout>
      <motion.div 
        className="space-y-8 py-8 w-full max-w-4xl"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="text-center space-y-2">
            <motion.h2 variants={itemVariants} className="text-5xl font-display font-black uppercase tracking-tight">Performance Review</motion.h2>
            <motion.p variants={itemVariants} className="text-xl text-muted-foreground font-medium">Here's how your teaching session went.</motion.p>
        </div>

        <div className="grid gap-8 md:grid-cols-12">
             {/* Grade Card */}
             <motion.div variants={itemVariants} className="md:col-span-4">
                <Card className="h-full flex flex-col items-center justify-center border-4 border-black shadow-neo-lg overflow-hidden relative bg-white">
                    <div className="absolute top-0 w-full h-8 bg-black flex items-center justify-center">
                        <span className="text-white font-mono font-bold text-xs uppercase tracking-widest">Final Grade</span>
                    </div>
                    <CardContent className="pt-12 pb-8 flex flex-col items-center">
                        <div className={cn(
                            "w-40 h-40 rounded-full border-4 border-black flex items-center justify-center shadow-neo transform rotate-[-5deg]",
                            getGradeColor(result.grade)
                        )}>
                            <span className="text-8xl font-black font-display tracking-tighter">{result.grade}</span>
                        </div>
                        {result.grade.startsWith('A') && <div className="mt-4 flex gap-2">
                             <PartyPopper className="text-accent w-8 h-8 animate-bounce" />
                             <PartyPopper className="text-primary w-8 h-8 animate-bounce delay-100" />
                        </div>}
                    </CardContent>
                </Card>
             </motion.div>

             {/* Feedback Card */}
             <motion.div variants={itemVariants} className="md:col-span-8">
                <Card className="h-full border-4 border-black shadow-neo bg-white relative">
                    <div className="absolute -top-3 -right-3 bg-accent border-2 border-black px-3 py-1 font-bold shadow-neo-sm transform rotate-3 z-10">
                        FEEDBACK
                    </div>
                    <CardHeader>
                        <CardTitle className="font-display text-2xl font-bold">Instructor Notes</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <p className="text-lg font-medium leading-relaxed border-l-4 border-secondary pl-4 py-2 bg-gray-50 rounded-r-md">
                            "{result.comments}"
                        </p>
                        
                        <div className="space-y-3">
                            {result.details.map((item, idx) => (
                                <motion.div 
                                    key={idx} 
                                    variants={itemVariants}
                                    className="flex items-center justify-between p-4 rounded-lg border-2 border-black shadow-neo-sm bg-white hover:translate-x-1 transition-transform"
                                >
                                    <span className="font-bold text-lg font-display">{item.point}</span>
                                    <div className="flex items-center gap-2">
                                        {item.status === 'correct' && <CheckCircle className="h-6 w-6 text-green-600 fill-green-100" />}
                                        {item.status === 'partial' && <AlertCircle className="h-6 w-6 text-yellow-600 fill-yellow-100" />}
                                        {item.status === 'wrong' && <AlertCircle className="h-6 w-6 text-red-600 fill-red-100" />}
                                        <span className={cn(
                                            "capitalize font-bold px-2 py-0.5 rounded-full text-xs border border-black",
                                            item.status === 'correct' ? "bg-green-100" :
                                            item.status === 'partial' ? "bg-yellow-100" : "bg-red-100"
                                        )}>
                                            {item.status}
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </CardContent>
                    <CardFooter className="bg-gray-50 border-t-2 border-black p-6">
                        <Button 
                            onClick={() => navigate('/topics', { state: { filename } })} 
                            className="ml-auto w-full md:w-auto text-lg py-6"
                        >
                            <RotateCcw className="mr-2 h-5 w-5" /> Back to Topics
                        </Button>
                    </CardFooter>
                </Card>
             </motion.div>
        </div>
      </motion.div>
    </Layout>
  );
};

export default Evaluation;
