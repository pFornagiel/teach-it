import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background font-sans antialiased flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {children}
      </div>
    </div>
  );
};

export default Layout;
