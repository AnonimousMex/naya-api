import { test as base, APIRequestContext, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const TEST_DATA_PATH = path.join(__dirname, '../test-data.json');

export interface TestData {
  api: {
    baseURL: string;
    timeout: number;
  };
  patient: {
    email: string;
    password: string;
    confirmPassword: string;
    name: string;
    newPassword: string;
    newConfirmPassword: string;
  };
  verification: {
    code: string;
    passwordResetCode: string;
  };
  therapist: {
    connectionCode: string;
  };
  profile: {
    animalId: string;
  };
}

let testData: TestData;

function loadTestData(): TestData {
  if (!testData) {
    const rawData = fs.readFileSync(TEST_DATA_PATH, 'utf-8');
    testData = JSON.parse(rawData);
  }
  return testData;
}

export interface TestFixtures {
  testData: TestData;
  apiContext: APIRequestContext;
}

export const test = base.extend<TestFixtures>({
  testData: async ({}, use) => {
    const data = loadTestData();
    await use(data);
  },

  apiContext: async ({ playwright }, use) => {
    const context = await playwright.request.newContext({
      baseURL: 'http://localhost:8000',
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    await use(context);
    await context.dispose();
  },
});

export { expect };
