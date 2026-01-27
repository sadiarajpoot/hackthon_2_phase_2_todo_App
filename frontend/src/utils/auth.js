import { atom } from 'jotai';

// Atom to track authentication status
export const isAuthenticatedAtom = atom(false);

// Atom to track user profile
export const userProfileAtom = atom(null);