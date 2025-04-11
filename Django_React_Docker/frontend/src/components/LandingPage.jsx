import React from "react";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center px-6">
      <div className="max-w-2xl text-center text-white">
        <h1 className="text-5xl font-extrabold mb-6">Welcome to Our Website</h1>
        <p className="text-xl mb-8">
          Discover our amazing services and start your journey with us today.
        </p>
        <a
          href="#get-started"
          className="inline-block bg-white text-blue-600 font-semibold px-6 py-3 rounded-full shadow-lg hover:bg-gray-100 transition"
        >
          Get Started
        </a>
      </div>
    </div>
  );
};

export default LandingPage;
