//https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javascriptv3/example_code/cognito-identity-provider/scenarios/cognito-developer-guide-react-example/frontend-client

import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
  SignUpCommand,
  ConfirmSignUpCommand,
 GetTokensFromRefreshTokenCommand,
 AuthFlowType
} from "@aws-sdk/client-cognito-identity-provider";
import { setTokens } from "@/Context";

// Get Cognito configuration from environment variables
const cognitoConfig = {
  region: import.meta.env.VITE_COGNITO_REGION || "us-east-1",
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  clientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
};

// Validate that required config is present
if (!cognitoConfig.userPoolId || !cognitoConfig.clientId) {
  console.error("Missing Cognito configuration. Please ensure VITE_COGNITO_USER_POOL_ID and VITE_COGNITO_CLIENT_ID are set.");
}

export const cognitoClient = new CognitoIdentityProviderClient({
  region: cognitoConfig.region,
});

export const signIn = async (username: string, password: string) => {
  const params = {
    AuthFlow: AuthFlowType.USER_PASSWORD_AUTH,
    ClientId: cognitoConfig.clientId,
    AuthParameters: {
      USERNAME: username,
      PASSWORD: password,
    },
  };
  try {
    const command = new InitiateAuthCommand(params);
    const { AuthenticationResult } = await cognitoClient.send(command);
    return AuthenticationResult;
  } catch (error) {
    console.error("Error signing in: ", error);
    throw error;
  }
};

export const signUp = async (username: string, email: string, password: string) => {
  const params = {
    ClientId: cognitoConfig.clientId,
    Username: username,
    Password: password,
    UserAttributes: [
      {
        Name: "email",
        Value: email,
      }
    ],
  };
  try {
    const command = new SignUpCommand(params);
    const response = await cognitoClient.send(command);
    console.log("Sign up success: ", response);
    return response;
  } catch (error) {
    console.error("Error signing up: ", error);
    throw error;
  }
};

export const confirmSignUp = async (username: string, code: string) => {
  const params = {
    ClientId: cognitoConfig.clientId,
    Username: username,
    ConfirmationCode: code,
  };
  try {
    const command = new ConfirmSignUpCommand(params);
    await cognitoClient.send(command);
    console.log("User confirmed successfully");
    return true;
  } catch (error) {
    console.error("Error confirming sign up: ", error);
    throw error;
  }
};

export const refreshTokens = async () => {
  const params = {
    ClientId: cognitoConfig.clientId,
    RefreshToken: localStorage.getItem("refreshToken") ?? undefined
  };
  try {
    const command = new GetTokensFromRefreshTokenCommand(params);
    const { AuthenticationResult } = await cognitoClient.send(command);
    if (AuthenticationResult) {
      setTokens(
        AuthenticationResult.IdToken || "",
        AuthenticationResult.AccessToken || "",
        AuthenticationResult.RefreshToken || ""
      );
      return AuthenticationResult;
    }
  } catch (error) {
    console.error("Error refreshing tokens: ", error);
    throw error;
  }
}