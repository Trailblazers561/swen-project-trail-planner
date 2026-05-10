import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signIn, signUp, confirmSignUp, resendConfirmationCode, forgotPassword, confirmForgotPassword } from "./authService";
import React from "react";
import { Button } from "@/components/ui/button";
import { Eye, EyeOff, CircleAlert, CircleCheck, Undo2, ArrowRight, LoaderCircle } from "lucide-react";
import { useAuth } from "@/Context";
import {
  UserNotConfirmedException,
  UserNotFoundException,
  NotAuthorizedException,
  UsernameExistsException,
  UserLambdaValidationException,
  CodeMismatchException,
  ExpiredCodeException,
  InvalidParameterException,
} from "@aws-sdk/client-cognito-identity-provider";

enum LoginMode {
  SIGN_IN,
  SIGN_UP,
  CONFIRM_ACCOUNT,
  FORGOT_PASSWORD,
  RESET_PASSWORD,
  RESEND_CODE
}

enum LoginError {
  UNKNOWN_ERROR, // Unknown what went wrong
  USER_NOT_FOUND, // User does not exist
  NOT_AUTHORIZED, // Incorrect username or password
  USER_NOT_CONFIRMED, // User is not confirmed
  USERNAME_EXISTS, // User already exists
  EMAIL_EXISTS, // Email already exists with verified user
  PASSWORD_MISMATCH, // Entered passwords don't match
  PASSWORD_SHORT, // Entered password too short
  CODE_MISMATCH, // The code is wrong
  EXPIRED_CODE, // The code is expired
}

const LoginPage = () => {
  const navigate = useNavigate();
  const { currentRole } = useAuth();
  let leavingPage = false;

  useEffect(() => {
    if (currentRole && !leavingPage) {
      leavingPage = true;
      navigate(-1);
    }
  }, [currentRole]);

  const [loginMode, setLoginMode] = useState(LoginMode.SIGN_IN);
  const [loginError, setLoginError] = useState<LoginError | null>(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");
  const [code, setCode] = useState("");
  const [resentCode, setResentCode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [destinationEmail, setDestinationEmail] = useState("your email");
  const { setAuth } = useAuth();

  useEffect(() => {
    setLoginError(null);
    setConfirmPassword("");
    setCode("");
    setResentCode(false);
  }, [loginMode]);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const session = await signIn(username, password);
      setLoading(false);
      setAuth(
        session?.IdToken || "",
        session?.AccessToken || "",
        session?.RefreshToken || ""
      );
      console.log("Sign in successful", session);
    } catch (error) {
      setLoading(false);
      if (error instanceof UserNotFoundException) {
        setLoginError(LoginError.USER_NOT_FOUND);
      } else if (error instanceof NotAuthorizedException) {
        setLoginError(LoginError.NOT_AUTHORIZED);
      } else if (error instanceof UserNotConfirmedException) {
        setLoginError(LoginError.USER_NOT_CONFIRMED);
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Sign in failed: ${error}`);
      }
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (password !== confirmPassword) {
        setLoginError(LoginError.PASSWORD_MISMATCH);
        return;
      }
      if (password.length < 6) {
        setLoginError(LoginError.PASSWORD_SHORT);
        return;
      }
      setLoading(true);
      const session = await signUp(username, email, password);
      setLoading(false);
      console.log("Sign up successful", session);
      setLoginMode(LoginMode.CONFIRM_ACCOUNT);
    } catch (error) {
      setLoading(false);
      if (error instanceof UsernameExistsException) {
        setLoginError(LoginError.USERNAME_EXISTS);
      } else if (error instanceof UserLambdaValidationException) {
        setLoginError(LoginError.EMAIL_EXISTS)
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Sign up failed: ${error}`);
      }
    }
  };

  const handleConfirmAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const session = await confirmSignUp(username, code);
      setLoading(false);
      console.log("Confirmation successful", session);
      setLoginMode(LoginMode.SIGN_IN);
    } catch (error) {
      setLoading(false);
      if (error instanceof CodeMismatchException) {
        setLoginError(LoginError.CODE_MISMATCH);
      } else if (error instanceof ExpiredCodeException) {
        setLoginError(LoginError.EXPIRED_CODE)
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Confirm account failed: ${error}`);
      }
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const session = await forgotPassword(username);
      setLoading(false);
      console.log("Forgot password code send successful", session);
      setDestinationEmail(session.CodeDeliveryDetails?.Destination ?? "your email")
      setPassword("");
      setLoginMode(LoginMode.RESET_PASSWORD);
    } catch (error) {
      setLoading(false);
      if (error instanceof UserNotFoundException) {
        setLoginError(LoginError.USER_NOT_FOUND);
      } else if (error instanceof UserNotConfirmedException) {
        setLoginError(LoginError.USER_NOT_CONFIRMED);
      } else if (error instanceof InvalidParameterException) {
        setLoginError(LoginError.USER_NOT_CONFIRMED); // Intentially not Invalid Parameter
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Forgot password failed: ${error}`);
      }
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (password !== confirmPassword) {
        setLoginError(LoginError.PASSWORD_MISMATCH);
        return;
      }
      if (password.length < 6) {
        setLoginError(LoginError.PASSWORD_SHORT);
        return;
      }
      setLoading(true);
      const session = await confirmForgotPassword(username, code, password);
      setLoading(false);
      console.log("Resend successful", session);
      setLoginMode(LoginMode.SIGN_IN);
    } catch (error) {
      setLoading(false);
      if (error instanceof CodeMismatchException) {
        setLoginError(LoginError.CODE_MISMATCH);
      } else if (error instanceof ExpiredCodeException) {
        setLoginError(LoginError.EXPIRED_CODE)
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Reset password failed: ${error}`);
      }
    }
  };

  const handleResendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const session = await resendConfirmationCode(username);
      setLoading(false);
      console.log("Resend successful", session);
      setLoginMode(LoginMode.CONFIRM_ACCOUNT);
    } catch (error) {
      setLoading(false);
      if (error instanceof UserNotFoundException) {
        setLoginError(LoginError.USER_NOT_FOUND);
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Resend code failed: ${error}`);
      }
    }
  };

  const resendVerificationCode = async () => {
    try {
      const session = await resendConfirmationCode(username);
      console.log("Resend successful", session);
    } catch (error) {
      if (error instanceof CodeMismatchException) {
        setLoginError(LoginError.CODE_MISMATCH);
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Resend verification code failed: ${error}`);
      }
    }
  }
  const resendPasswordCode = async () => {
    try {
      const session = await forgotPassword(username);
      console.log("Resend password code send successful", session);
      setDestinationEmail(session.CodeDeliveryDetails?.Destination ?? "your email")
      setLoginMode(LoginMode.RESET_PASSWORD);
    } catch (error) {
      setLoading(false);
      if (error instanceof UserNotFoundException) {
        setLoginError(LoginError.USER_NOT_FOUND);
      } else if (error instanceof UserNotConfirmedException) {
        setLoginError(LoginError.USER_NOT_CONFIRMED);
      } else if (error instanceof InvalidParameterException) {
        setLoginError(LoginError.USER_NOT_CONFIRMED); // Intentially not Invalid Parameter
      } else {
        setLoginError(LoginError.UNKNOWN_ERROR);
        alert(`Resend password code failed: ${error}`);
      }
    }
  }
  useEffect(() => {
    if (resentCode)
      if (loginMode === LoginMode.CONFIRM_ACCOUNT)
        resendVerificationCode();
      else if (loginMode == LoginMode.RESET_PASSWORD)
        resendPasswordCode();
  }, [resentCode]);

  return (
    <div className="flex h-screen">

      <div
        className="fixed left-0 top-0 h-screen w-11/16 bg-cover bg-center"
        style={{ backgroundImage: "url('/News-OswegatchieRiver-BearPond.jpg')" }}
      >
        <div className="absolute inset-0 bg-black/20" />
        <img
          src="/AWA-logo.png"
          alt="Logo"
          className="absolute top-8 left-1/2 w-56 md:w-64 -translate-x-1/2"
        />
      </div>

      {loading && (<LoaderCircle size={200} strokeWidth={2} className="absolute text-5xl text-navbar m-auto left-27/32 animate-spin  -translate-x-1/2 top-1/2 -translate-y-50 z-500" />)}
      {loading && (<div className="fixed right-0 top-0 h-screen w-5/16  bg-black/40 z-499"></div>)}
      <div className="fixed right-0 top-0 h-screen w-5/16 flex items-center justify-center">
        <div className="flex w-full max-w-4xl items-start" id="loginForm">
          {loginMode == LoginMode.SIGN_IN && (
            <div className="flex-1 px-10 pt-6 h-124">
              <h2 className="text-2xl font-semibold mb-2">Welcome Back</h2>
              <p className="text-gray-500 mb-6">Sign in to your account</p>
              <form onSubmit={handleSignIn} className="space-y-4">
                {loginError !== null && (
                  <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-50 p-4 text-red-800">
                    <div className="mt-0.5">
                      <CircleAlert size={30} />
                    </div>
                    <div className="text-left">
                      <span className="text-lg font-semibold mb-1">There was a problem</span>
                      {loginError === LoginError.USER_NOT_FOUND ? (
                        <p className="text-sm text-red-700">
                          No account was found with the specified email
                        </p>
                      ) : loginError === LoginError.NOT_AUTHORIZED ? (
                        <p className="text-sm text-red-700">
                          Incorrect email or password
                        </p>
                      ) : loginError === LoginError.USER_NOT_CONFIRMED ? (
                        <>
                          <p className="text-sm text-red-700">
                            Please verify your email before logging in
                          </p>
                          <button
                            type="button"
                            onClick={() => setLoginMode(LoginMode.RESEND_CODE)}
                            className="text-sm hover:underline cursor-pointer"
                          >
                            Resend code?
                          </button>
                        </>
                      ) : (
                        <p className="text-sm text-red-700">
                          An error has occured
                        </p>
                      )}
                    </div>
                  </div>
                )}
                <input
                  type="text"
                  placeholder="Username or Email"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <div>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                      required
                    />
                    <span
                      onMouseLeave={() => setShowPassword(false)}
                      onMouseDown={() => setShowPassword(true)}
                      onMouseUp={() => setShowPassword(false)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                    </span>
                  </div>
                  <div className="text-right text-sm">
                    <button
                      type="button"
                      onClick={() => setLoginMode(LoginMode.FORGOT_PASSWORD)}
                      className="text-dark-yellow-green hover:underline cursor-pointer"
                    >
                      Forgot password?
                    </button>
                  </div>
                </div>
                <Button type="submit" variant="primary" className="w-full">
                  Login
                </Button>
              </form>
              <div className="text-sm flex justify-between mt-10 border py-2 px-3 rounded-md">
                <span className="text-left">Dont have an account?</span>
                <button
                  type="button"
                  onClick={() => {
                    setLoginMode(LoginMode.SIGN_UP);
                    setUsername("");
                    setPassword("");
                  }}
                  className="flex text-dark-yellow-green hover:underline cursor-pointer  items-center text-right"
                >
                  Create an account{<ArrowRight size={18} />}
                </button>
              </div>
            </div>
          )}
          {loginMode == LoginMode.SIGN_UP && (
            <div className="flex-1 px-10 pt-6 h-124">
              <h2 className="text-2xl font-semibold mb-2">Get Started</h2>
              <p className="text-gray-500 mb-6">Register an account</p>
              <form onSubmit={handleSignUp} className="space-y-4">
                {loginError !== null && (
                  <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-50 p-4 text-red-800">
                    <div className="mt-0.5">
                      <CircleAlert size={30} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold mb-1">There was a problem</h3>
                      {loginError === LoginError.USERNAME_EXISTS ? (
                        <p className="text-sm text-red-700">
                          Enterd username is already taken
                        </p>
                      ) : loginError === LoginError.EMAIL_EXISTS ? (
                        <p className="text-sm text-red-700">
                          Enterd email is already taken
                        </p>
                      ) : loginError === LoginError.PASSWORD_MISMATCH ? (
                        <p className="text-sm text-red-700">
                          Entered passwords do not match
                        </p>
                      ) : loginError === LoginError.PASSWORD_SHORT ? (
                        <p className="text-sm text-red-700">
                          Password must be a minimum of six characters
                        </p>
                      ) : (
                        <p className="text-sm text-red-700">
                          An error has occured
                        </p>
                      )}
                    </div>
                  </div>
                )}
                <input
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                  <span
                    onMouseLeave={() => setShowPassword(false)}
                    onMouseDown={() => setShowPassword(true)}
                    onMouseUp={() => setShowPassword(false)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                  </span>
                </div>
                <input
                  type="password"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <Button className="w-full" variant="primary">
                  Sign Up
                </Button>
                <div className="text-left ">
                  <button
                    type="button"
                    onClick={() => setLoginMode(LoginMode.SIGN_IN)}
                    className="text-sm flex text-dark hover:underline cursor-pointer gap-1 items-center"
                  >
                    {<Undo2 size={18} />}Sign In
                  </button>
                </div>
              </form>
            </div>
          )}
          {loginMode == LoginMode.CONFIRM_ACCOUNT && (
            <div className="flex-1 px-10 pt-6 h-124">
              <h2 className="text-2xl font-semibold mb-2">Confirm Account</h2>
              <p className="text-gray-500 mb-6">To verify your email, we've sent a code to {email}</p>
              <form onSubmit={handleConfirmAccount} className="space-y-4">
                {loginError !== null && (
                  <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-50 p-4 text-red-800">
                    <div className="mt-0.5">
                      <CircleAlert size={30} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold mb-1">There was a problem</h3>
                      {loginError === LoginError.CODE_MISMATCH ? (
                        <p className="text-sm text-red-700">
                          Provided code is incorrect
                        </p>
                      ) : loginError === LoginError.EXPIRED_CODE ? (
                        <p className="text-sm text-red-700">
                          Provided code is expired, please request a new one
                        </p>
                      ) : (
                        <p className="text-sm text-red-700">
                          An error has occured
                        </p>
                      )}
                    </div>
                  </div>
                )}
                <div>
                  <input
                    type="text"
                    placeholder="Code"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                  <div className="flex justify-between text-sm mt-0.5">
                    <div className="flex items-center gap-1 text-green-700">
                      {resentCode && (
                        <>
                          <CircleCheck size={15} />
                          <h3 className="">
                            A new code has been sent</h3>
                        </>
                      )}
                    </div>
                    <div className="text-right text-sm">
                      <button
                        type="button"
                        onClick={() => setResentCode(true)}
                        className="text-dark-yellow-green hover:underline cursor-pointer"
                      >
                        Resend code
                      </button>
                    </div>
                  </div>
                </div>
                <Button className="w-full" variant="primary">
                  Confirm Account
                </Button>
                <div className="text-left ">
                  <button
                    type="button"
                    onClick={() => setLoginMode(LoginMode.SIGN_UP)}
                    className="text-sm flex text-dark hover:underline cursor-pointer gap-1 items-center"
                  >
                    {<Undo2 size={18} />}Sign Up
                  </button>
                </div>
              </form>
            </div>
          )}
          {loginMode == LoginMode.FORGOT_PASSWORD && (
            <div className="flex-1 px-10 pt-6 h-124">
              <h2 className="text-2xl font-semibold mb-2">Reset Password</h2>
              <p className="text-gray-500 mb-6">Enter the username or email associated with your account</p>

              <form onSubmit={handleForgotPassword} className="space-y-4">
                {loginError !== null && (
                  <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-50 p-4 text-red-800">
                    <div className="mt-0.5">
                      <CircleAlert size={30} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold mb-1">There was a problem</h3>
                      {loginError === LoginError.USER_NOT_FOUND ? (
                        <p className="text-sm text-red-700">
                          No account was found with the specified username or email
                        </p>
                      ) : loginError === LoginError.USER_NOT_CONFIRMED ? (
                        <>
                          <p className="text-sm text-red-700">
                            Please verify your email before resetting your password
                          </p>
                          <button
                            type="button"
                            onClick={() => {
                              setUsername("");
                              setLoginMode(LoginMode.RESEND_CODE);
                            }}
                            className="text-sm hover:underline cursor-pointer"
                          >
                            Resend code?
                          </button>
                        </>
                      ) : (
                        <p className="text-sm text-red-700">
                          An error has occured
                        </p>
                      )}
                    </div>
                  </div>
                )}
                <input
                  type="text"
                  placeholder="Username or Email"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <Button type="submit" variant="primary" className="w-full">
                  Continue
                </Button>
                <div className="text-left ">
                  <button
                    type="button"
                    onClick={() => setLoginMode(LoginMode.SIGN_IN)}
                    className="text-sm flex text-dark hover:underline cursor-pointer gap-1 items-center"
                  >
                    {<Undo2 size={18} />}Sign In
                  </button>
                </div>
              </form>
            </div>
          )}
          {loginMode == LoginMode.RESET_PASSWORD && (
            <div className="flex-1 px-10 pt-6 h-124">
              <h2 className="text-2xl font-semibold mb-2">Reset Password</h2>
              <p className="text-gray-500 mb-6">To reset your password, we've sent a code to {destinationEmail}</p>

              <form onSubmit={handleResetPassword} className="space-y-4">
                {loginError !== null && (
                  <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-50 p-4 text-red-800">
                    <div className="mt-0.5">
                      <CircleAlert size={30} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold mb-1">There was a problem</h3>
                      {loginError === LoginError.CODE_MISMATCH ? (
                        <p className="text-sm text-red-700">
                          Provided code is incorrect
                        </p>
                      ) : loginError === LoginError.EXPIRED_CODE ? (
                        <p className="text-sm text-red-700">
                          Provided code is expired, please request a new one
                        </p>
                      ) : loginError === LoginError.PASSWORD_MISMATCH ? (
                        <p className="text-sm text-red-700">
                          Entered passwords do not match
                        </p>
                      ) : loginError === LoginError.PASSWORD_SHORT ? (
                        <p className="text-sm text-red-700">
                          Password must be a minimum of six characters
                        </p>
                      ) : (
                        <p className="text-sm text-red-700">
                          An error has occured
                        </p>
                      )}
                    </div>
                  </div>
                )}
                <div>
                  <input
                    type="text"
                    placeholder="Code"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                  <div className="flex justify-between text-sm mt-0.5">
                    <div className="flex items-center gap-1 text-green-700">
                      {resentCode && (
                        <>
                          <CircleCheck size={15} />
                          <h3 className="">
                            A new code has been sent</h3>
                        </>
                      )}
                    </div>
                    <div className="text-right text-sm">
                      <button
                        type="button"
                        onClick={() => setResentCode(true)}
                        className="text-dark-yellow-green hover:underline cursor-pointer"
                      >
                        Resend code
                      </button>
                    </div>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                  <span
                    onMouseLeave={() => setShowPassword(false)}
                    onMouseDown={() => setShowPassword(true)}
                    onMouseUp={() => setShowPassword(false)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                  </span>
                </div>
                <input
                  type="password"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <Button type="submit" variant="primary" className="w-full">
                  Reset Password
                </Button>
                <div className="text-left ">
                  <button
                    type="button"
                    onClick={() => setLoginMode(LoginMode.SIGN_IN)}
                    className="text-sm flex text-dark hover:underline cursor-pointer gap-1 items-center"
                  >
                    {<Undo2 size={18} />}Sign In
                  </button>
                </div>
              </form>
            </div>
          )}
          {loginMode == LoginMode.RESEND_CODE && (
            <div className="flex-1 px-10 pt-6 h-124">
              <h2 className="text-2xl font-semibold mb-2">Resend Code</h2>
              <p className="text-gray-500 mb-6">Enter the username associated with your account</p>
              <form onSubmit={handleResendCode} className="space-y-4">
                {loginError !== null && (
                  <div className="flex items-center gap-3 rounded-lg border border-red-800 bg-red-50 p-4 text-red-800">
                    <div className="mt-0.5">
                      <CircleAlert size={30} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold mb-1">There was a problem</h3>
                      {/* Update this to whatever errors actually get thrown for resend code auth */}
                      {loginError === LoginError.USER_NOT_FOUND ? (
                        <p className="text-sm text-red-700">
                          No account was found with the specified username
                        </p>
                      ) : (
                        <p className="text-sm text-red-700">
                          An error has occured
                        </p>
                      )}
                    </div>
                  </div>
                )}
                <input
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
                <Button type="submit" variant="primary" className="w-full">
                  Resend Code
                </Button>
                <div className="text-left ">
                  <button
                    type="button"
                    onClick={() => setLoginMode(LoginMode.SIGN_IN)}
                    className="text-sm flex text-dark hover:underline cursor-pointer gap-1 items-center"
                  >
                    {<Undo2 size={18} />}Sign In
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;