import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthForm } from '../auth-form'

// Mock the auth store
jest.mock('@/store/auth-store', () => ({
    useAuthStore: () => ({
        login: jest.fn(),
        register: jest.fn(),
        isLoading: false,
        error: null,
    }),
}))

describe('AuthForm', () => {
    const defaultProps = {
        mode: 'login' as const,
        onSuccess: jest.fn(),
    }

    beforeEach(() => {
        jest.clearAllMocks()
    })

    describe('Login Mode', () => {
        it('renders login form correctly', () => {
            render(<AuthForm {...defaultProps} />)

            expect(screen.getByText(/sign in/i)).toBeInTheDocument()
            expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
            expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
            expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
            expect(screen.getByText(/don't have an account/i)).toBeInTheDocument()
        })

        it('validates required fields', async () => {
            render(<AuthForm {...defaultProps} />)

            const submitButton = screen.getByRole('button', { name: /sign in/i })
            fireEvent.click(submitButton)

            await waitFor(() => {
                expect(screen.getByText(/email is required/i)).toBeInTheDocument()
                expect(screen.getByText(/password is required/i)).toBeInTheDocument()
            })
        })

        it('validates email format', async () => {
            render(<AuthForm {...defaultProps} />)

            const emailInput = screen.getByLabelText(/email/i)
            const submitButton = screen.getByRole('button', { name: /sign in/i })

            fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
            fireEvent.click(submitButton)

            await waitFor(() => {
                expect(screen.getByText(/invalid email format/i)).toBeInTheDocument()
            })
        })

        it('submits form with valid data', async () => {
            const mockLogin = jest.fn()
            jest.mocked(require('@/store/auth-store').useAuthStore).mockReturnValue({
                login: mockLogin,
                register: jest.fn(),
                isLoading: false,
                error: null,
            })

            render(<AuthForm {...defaultProps} />)

            const emailInput = screen.getByLabelText(/email/i)
            const passwordInput = screen.getByLabelText(/password/i)
            const submitButton = screen.getByRole('button', { name: /sign in/i })

            await userEvent.type(emailInput, 'test@example.com')
            await userEvent.type(passwordInput, 'password123')
            fireEvent.click(submitButton)

            await waitFor(() => {
                expect(mockLogin).toHaveBeenCalledWith({
                    email: 'test@example.com',
                    password: 'password123',
                })
            })
        })
    })

    describe('Register Mode', () => {
        const registerProps = {
            ...defaultProps,
            mode: 'register' as const,
        }

        it('renders register form correctly', () => {
            render(<AuthForm {...registerProps} />)

            expect(screen.getByText(/create account/i)).toBeInTheDocument()
            expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
            expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
            expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
            expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
            expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
            expect(screen.getByText(/already have an account/i)).toBeInTheDocument()
        })

        it('validates password confirmation', async () => {
            render(<AuthForm {...registerProps} />)

            const passwordInput = screen.getByLabelText(/password/i)
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
            const submitButton = screen.getByRole('button', { name: /create account/i })

            await userEvent.type(passwordInput, 'password123')
            await userEvent.type(confirmPasswordInput, 'differentpassword')
            fireEvent.click(submitButton)

            await waitFor(() => {
                expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
            })
        })

        it('validates username length', async () => {
            render(<AuthForm {...registerProps} />)

            const usernameInput = screen.getByLabelText(/username/i)
            const submitButton = screen.getByRole('button', { name: /create account/i })

            fireEvent.change(usernameInput, { target: { value: 'ab' } })
            fireEvent.click(submitButton)

            await waitFor(() => {
                expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument()
            })
        })

        it('submits registration form with valid data', async () => {
            const mockRegister = jest.fn()
            jest.mocked(require('@/store/auth-store').useAuthStore).mockReturnValue({
                login: jest.fn(),
                register: mockRegister,
                isLoading: false,
                error: null,
            })

            render(<AuthForm {...registerProps} />)

            const emailInput = screen.getByLabelText(/email/i)
            const usernameInput = screen.getByLabelText(/username/i)
            const passwordInput = screen.getByLabelText(/password/i)
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
            const submitButton = screen.getByRole('button', { name: /create account/i })

            await userEvent.type(emailInput, 'test@example.com')
            await userEvent.type(usernameInput, 'testuser')
            await userEvent.type(passwordInput, 'password123')
            await userEvent.type(confirmPasswordInput, 'password123')
            fireEvent.click(submitButton)

            await waitFor(() => {
                expect(mockRegister).toHaveBeenCalledWith({
                    email: 'test@example.com',
                    username: 'testuser',
                    password: 'password123',
                    role: 'patient',
                })
            })
        })
    })

    describe('Form State', () => {
        it('shows loading state during submission', () => {
            jest.mocked(require('@/store/auth-store').useAuthStore).mockReturnValue({
                login: jest.fn(),
                register: jest.fn(),
                isLoading: true,
                error: null,
            })

            render(<AuthForm {...defaultProps} />)

            expect(screen.getByText(/loading/i)).toBeInTheDocument()
            expect(screen.getByRole('button', { name: /loading/i })).toBeDisabled()
        })

        it('displays error messages from store', () => {
            const errorMessage = 'Invalid credentials'
            jest.mocked(require('@/store/auth-store').useAuthStore).mockReturnValue({
                login: jest.fn(),
                register: jest.fn(),
                isLoading: false,
                error: errorMessage,
            })

            render(<AuthForm {...defaultProps} />)

            expect(screen.getByText(errorMessage)).toBeInTheDocument()
        })

        it('clears error when form is submitted again', async () => {
            const mockLogin = jest.fn()
            const mockStore = {
                login: mockLogin,
                register: jest.fn(),
                isLoading: false,
                error: 'Previous error',
            }

            jest.mocked(require('@/store/auth-store').useAuthStore).mockReturnValue(mockStore)

            render(<AuthForm {...defaultProps} />)

            // Error should be visible initially
            expect(screen.getByText('Previous error')).toBeInTheDocument()

            // Fill form and submit
            const emailInput = screen.getByLabelText(/email/i)
            const passwordInput = screen.getByLabelText(/password/i)
            const submitButton = screen.getByRole('button', { name: /sign in/i })

            await userEvent.type(emailInput, 'test@example.com')
            await userEvent.type(passwordInput, 'password123')
            fireEvent.click(submitButton)

            // Error should be cleared after submission
            await waitFor(() => {
                expect(mockLogin).toHaveBeenCalled()
            })
        })
    })

    describe('Accessibility', () => {
        it('has proper form labels and associations', () => {
            render(<AuthForm {...defaultProps} />)

            const emailInput = screen.getByLabelText(/email/i)
            const passwordInput = screen.getByLabelText(/password/i)

            expect(emailInput).toHaveAttribute('type', 'email')
            expect(passwordInput).toHaveAttribute('type', 'password')
            expect(emailInput).toHaveAttribute('required')
            expect(passwordInput).toHaveAttribute('required')
        })

        it('supports keyboard navigation', async () => {
            render(<AuthForm {...defaultProps} />)

            const emailInput = screen.getByLabelText(/email/i)
            const passwordInput = screen.getByLabelText(/password/i)
            const submitButton = screen.getByRole('button', { name: /sign in/i })

            // Tab through form elements
            emailInput.focus()
            expect(emailInput).toHaveFocus()

            passwordInput.focus()
            expect(passwordInput).toHaveFocus()

            submitButton.focus()
            expect(submitButton).toHaveFocus()
        })
    })
})
