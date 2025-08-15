import type { Meta, StoryObj } from '@storybook/react'
import { AuthForm } from './auth-form'

const meta: Meta<typeof AuthForm> = {
    title: 'Components/Auth/AuthForm',
    component: AuthForm,
    parameters: {
        layout: 'centered',
        docs: {
            description: {
                component: 'A form component for user authentication (login/register) with validation and error handling.',
            },
        },
    },
    argTypes: {
        mode: {
            control: { type: 'select' },
            options: ['login', 'register'],
            description: 'The mode of the form (login or register)',
        },
        onSuccess: {
            action: 'success',
            description: 'Callback function called on successful authentication',
        },
    },
    tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof meta>

export const Login: Story = {
    args: {
        mode: 'login',
        onSuccess: () => console.log('Login successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Default login form with email and password fields.',
            },
        },
    },
}

export const Register: Story = {
    args: {
        mode: 'register',
        onSuccess: () => console.log('Registration successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Registration form with email, username, password, and confirmation fields.',
            },
        },
    },
}

export const Loading: Story = {
    args: {
        mode: 'login',
        onSuccess: () => console.log('Login successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Form in loading state during authentication.',
            },
        },
    },
    decorators: [
        (Story) => {
            // Mock the auth store to show loading state
            jest.doMock('@/store/auth-store', () => ({
                useAuthStore: () => ({
                    login: jest.fn(),
                    register: jest.fn(),
                    isLoading: true,
                    error: null,
                }),
            }))
            return <Story />
        },
    ],
}

export const WithError: Story = {
    args: {
        mode: 'login',
        onSuccess: () => console.log('Login successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Form displaying an error message from the authentication process.',
            },
        },
    },
    decorators: [
        (Story) => {
            // Mock the auth store to show error state
            jest.doMock('@/store/auth-store', () => ({
                useAuthStore: () => ({
                    login: jest.fn(),
                    register: jest.fn(),
                    isLoading: false,
                    error: 'Invalid email or password',
                }),
            }))
            return <Story />
        },
    ],
}

export const ValidationErrors: Story = {
    args: {
        mode: 'register',
        onSuccess: () => console.log('Registration successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Form showing validation errors for invalid input.',
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement)

        // Submit form without filling required fields
        const submitButton = canvas.getByRole('button', { name: /create account/i })
        await userEvent.click(submitButton)

        // Wait for validation errors to appear
        await waitFor(() => {
            expect(canvas.getByText(/email is required/i)).toBeInTheDocument()
            expect(canvas.getByText(/username is required/i)).toBeInTheDocument()
            expect(canvas.getByText(/password is required/i)).toBeInTheDocument()
        })
    },
}

export const DarkMode: Story = {
    args: {
        mode: 'login',
        onSuccess: () => console.log('Login successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Form displayed in dark mode theme.',
            },
        },
        backgrounds: {
            default: 'dark',
        },
    },
    decorators: [
        (Story) => (
            <div className="dark">
                <Story />
            </div>
        ),
    ],
}

export const Mobile: Story = {
    args: {
        mode: 'login',
        onSuccess: () => console.log('Login successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Form displayed on mobile device viewport.',
            },
        },
        viewport: {
            defaultViewport: 'mobile1',
        },
    },
}

export const Tablet: Story = {
    args: {
        mode: 'login',
        onSuccess: () => console.log('Login successful'),
    },
    parameters: {
        docs: {
            description: {
                story: 'Form displayed on tablet device viewport.',
            },
        },
        viewport: {
            defaultViewport: 'tablet',
        },
    },
}
