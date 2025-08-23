import { useEffect, useRef } from 'react';

export const useTimer = () => {
    const timersRef = useRef<Array<NodeJS.Timeout>>([]);

    const setTimeout = (callback: () => void, delay: number) => {
        const timer = global.setTimeout(callback, delay);
        timersRef.current.push(timer);
        return timer;
    };

    const setInterval = (callback: () => void, delay: number) => {
        const timer = global.setInterval(callback, delay);
        timersRef.current.push(timer);
        return timer;
    };

    const clearAllTimers = () => {
        timersRef.current.forEach(timer => {
            clearTimeout(timer);
            clearInterval(timer);
        });
        timersRef.current = [];
    };

    useEffect(() => {
        return clearAllTimers;
    }, []);

    return { setTimeout, setInterval, clearAllTimers };
};
