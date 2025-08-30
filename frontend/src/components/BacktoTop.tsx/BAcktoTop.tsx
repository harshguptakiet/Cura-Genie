"use client";
import React, { useEffect, useState } from "react";
import "./BacktoTop.css";

const BacktoTop: React.FC = () => {
    const [visible, setVisible] = useState(false);
    const [hasMounted, setHasMounted] = useState(false);

    useEffect(() => {
        setHasMounted(true);
        const handleScroll = () => {
            if (window.scrollY > 200) {
                setVisible(true);
            } else {
                setVisible(false);
            }
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    if (!hasMounted) return null;

    return (
        <button
            id="scrollToTopBtn"
            className="top-button"
            style={{ display: visible ? "block" : "none" }}
            onClick={scrollToTop}
        >
            ↑
        </button>
    );
};

export default BacktoTop;