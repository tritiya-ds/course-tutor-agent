import { Routes, Route } from "react-router-dom";
import { SignIn, SignUp } from "@clerk/react";
import { Toaster } from "@/components/ui/sonner";
import ClerkAuthProvider from "@/components/auth/ClerkAuthProvider";
import Home from "@/pages/Home";
import Quiz from "@/pages/Quiz";
import Instructor from "@/pages/Instructor";
import Evaluation from "@/pages/Evaluation";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  return (
    <ClerkAuthProvider>
      <Toaster richColors />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/instructor" element={<Instructor />} />
        <Route path="/evaluation" element={<Evaluation />} />
        <Route path="/sign-in/*" element={<div className="flex min-h-svh items-center justify-center bg-[#0b0d11] p-6"><SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" withSignUp /></div>} />
        <Route path="/sign-up/*" element={<div className="flex min-h-svh items-center justify-center bg-[#0b0d11] p-6"><SignUp routing="path" path="/sign-up" signInUrl="/sign-in" /></div>} />
      </Routes>
    </ClerkAuthProvider>
  );
}
