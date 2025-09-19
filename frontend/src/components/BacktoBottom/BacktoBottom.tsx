"use client";
import React, { useEffect, useState } from "react";
import "./BacktoBottom.css";

const BacktoBottom: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const toggleVisibility = () => {
      // Show button if NOT at bottom
      if (window.innerHeight + window.scrollY < document.body.offsetHeight - 200) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", toggleVisibility);
    return () => window.removeEventListener("scroll", toggleVisibility);
  }, []);

  const scrollToBottom = () => {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  };

  return (
    <>
      {isVisible && (
        <button className="back-to-bottom" onClick={scrollToBottom}>
          ↓
        </button>
      )}
    </>
  );
};

export default BacktoBottom;
