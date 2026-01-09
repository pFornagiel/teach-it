import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Upload, Loader2 } from 'lucide-react';
import { motion, type Variants } from 'framer-motion';

const Welcome: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleFiles = async (files: FileList | File[]) => {
    if (files.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();
    // Append all files to FormData
    Array.from(files).forEach(file => {
        formData.append('file', file);
    });

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        // Mock slight delay for effect
        setTimeout(() => {
          navigate('/topics', { state: { filename: file.name } });
        }, 1500);
         const data = await response.json();
         // Mock slight delay for effect
         setTimeout(() => {
            navigate('/topics', { state: { filenames: data.filenames } });
         }, 1500); 
      } else {
        console.error('Upload failed');
        setIsUploading(false);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setIsUploading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
        handleFiles(event.target.files);
    }
  };

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants: Variants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: 'spring', stiffness: 100 }
    }
  };

  if (isUploading) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center space-y-6 h-[60vh]">
          <div className="w-24 h-24 bg-secondary rounded-full border-4 border-black flex items-center justify-center animate-bounce shadow-neo">
            <Loader2 className="h-12 w-12 animate-spin text-black" />
          </div>
          <h2 className="text-3xl font-display font-bold">Uploading & Analyzing...</h2>
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

  return (
    <Layout>
      <motion.div
        className="space-y-12 py-8 relative min-h-[80vh] flex flex-col justify-center"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Hero Section */}
        <section className="text-center space-y-6">
          <motion.div variants={itemVariants} className="relative z-10 max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-7xl font-display font-black leading-[0.9] text-black">
              If you want to master something, <span className="bg-neo-pink px-2 border-2 border-black shadow-neo-sm transform -skew-x-6 inline-block">teach it.</span>
            </h1>
            <p className="mt-4 text-lg font-bold font-mono uppercase tracking-widest text-muted-foreground">
              — Richard Feynman
            </p>

            <p className="mt-8 text-xl md:text-2xl font-medium max-w-2xl mx-auto text-muted-foreground leading-relaxed">
              With <span className="font-bold text-black bg-secondary px-1 border-2 border-black">Teach.it</span>, you don't just study. You explain, you engage, and you excel. Upload your notes and let the AI challenge your understanding.
            </p>
          </motion.div>
            <motion.div variants={itemVariants} className="relative z-10 max-w-4xl mx-auto">
                <h1 className="text-5xl md:text-7xl font-display font-black leading-[0.9] text-black">
                    If you want to master something, <span className="bg-secondary px-2 border-2 border-black shadow-neo-sm transform -skew-x-6 inline-block">teach it.</span>
                </h1>
                <p className="mt-4 text-lg font-bold font-mono uppercase tracking-widest text-muted-foreground">
                    — Richard Feynman
                </p>
                
                <p className="mt-8 text-xl md:text-2xl font-medium max-w-2xl mx-auto text-muted-foreground leading-relaxed">
                    With <span className="font-bold text-black bg-secondary px-1 border-2 border-black">Teach.it</span>, you don't just study. You explain, you engage, and you excel. Upload your notes and let the AI challenge your understanding.
                </p>
            </motion.div>
        </section>

        {/* Upload Section - Regular Box (No OS Window) */}
        <motion.div variants={itemVariants} className="max-w-xl mx-auto w-full">
          <Card className="border-4 border-black shadow-neo-lg bg-white overflow-hidden p-8 md:p-10 hover:scale-[1.01] transition-transform duration-300">
            <div
              className={`
                        border-4 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer
                        flex flex-col items-center gap-4 bg-background group
                        ${isHovering ? 'border-primary bg-primary/5' : 'border-gray-300'}
                    `}
              onDragOver={(e) => { e.preventDefault(); setIsHovering(true); }}
              onDragLeave={() => setIsHovering(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsHovering(false);
                if (e.dataTransfer.files?.[0]) {
                  fileInputRef.current?.click();
                }
              }}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="w-16 h-16 bg-accent rounded-full border-4 border-black shadow-neo flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8" />
              </div>

              <div className="space-y-1">
                <h3 className="text-xl font-bold font-display">
                  Upload Knowledge Base
                </h3>
                <p className="text-sm text-muted-foreground font-medium">
                  Drag & Drop or Click to Browse
                </p>
              </div>

              <Button
                className="mt-2 text-base px-6 py-4 font-black uppercase tracking-widest border-2 w-full"
                variant="default"
              >
                Select File
              </Button>

              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".txt,.md,.csv,.docx,.jpg,.jpeg,.png,.gif,.webp"
                onChange={handleFileUpload}
              />
            </div>
          </Card>
                    onDragOver={(e) => { e.preventDefault(); setIsHovering(true); }}
                    onDragLeave={() => setIsHovering(false)}
                    onDrop={(e) => {
                        e.preventDefault();
                        setIsHovering(false);
                        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                            handleFiles(e.dataTransfer.files);
                        }
                    }}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <div className="w-16 h-16 bg-accent rounded-full border-4 border-black shadow-neo flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                            <Upload className="w-8 h-8" />
                    </div>
                    
                    <div className="space-y-1">
                        <h3 className="text-xl font-bold font-display">
                            Upload Knowledge Base
                        </h3>
                        <p className="text-sm text-muted-foreground font-medium">
                            Drag & Drop multiple files or Click to Browse
                        </p>
                    </div>

                    <Button 
                        className="mt-2 text-base px-6 py-4 font-black uppercase tracking-widest border-2 w-full" 
                        variant="default"
                    >
                        Select Files
                    </Button>
                    
                    <input 
                        type="file" 
                        ref={fileInputRef}
                        className="hidden" 
                        accept=".txt,.md,.pdf" 
                        multiple
                        onChange={handleFileUpload}
                    />
                </div>
            </Card>
        </motion.div>

        {/* Bottom Right Branding */}
        <div className="fixed bottom-8 right-8 z-50">
          <div className="bg-white border-2 border-black px-4 py-2 shadow-neo font-black font-display text-xl transform rotate-[-3deg] hover:rotate-0 transition-transform cursor-default">
            Teach.it
          </div>
             <div className="bg-secondary border-2 border-black px-4 py-2 shadow-neo font-display text-xl transform rotate-[-3deg] hover:rotate-0 transition-transform cursor-default">
                Teach.it
             </div>
        </div>

      </motion.div>
    </Layout>
  );
};

export default Welcome;
