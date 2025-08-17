// Copyright (C) 2025 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'

const execAsync = promisify(exec)

const isWindows = navigator.platform === 'Win32' ? true : false
export async function GET() {
  if (isWindows) {
    const worker = path.resolve(path.dirname(''), '../workers/get-camera-list')
    const virtualEnvPath = path.join(worker, 'venv', 'Scripts', 'python.exe')
    const scriptPath = path.join(worker, 'main.py')
    const command = virtualEnvPath + ' ' + scriptPath
    try {
      const { stdout } = await execAsync(command)
      const lines = stdout.split('\n').filter((line) => line.trim() !== '')

      const devices: { [key: string]: number } = {}
      let currentDeviceName = ''
      let index = 0

      for (const line of lines) {
        if (!line.startsWith('\t')) {
          // Device name line
          currentDeviceName = line.trim()
          devices[currentDeviceName] = index++
        }
      }
      return new Response(JSON.stringify({ devices }), { status: 200 })
    } catch (err: unknown) {
      console.error(`Error executing command: ${err}`)
      return new Response(JSON.stringify({ devices: [] }), { status: 200 })
    }
  } else {
    try {
      const { stdout } = await execAsync('v4l2-ctl --list-devices')
      const lines = stdout.split('\n').filter((line) => line.trim() !== '')

      const devices: { [key: string]: number } = {}
      let currentDeviceName = ''
      let index = 0

      for (const line of lines) {
        if (!line.startsWith('\t')) {
          // Device name line
          currentDeviceName = line.trim()
          devices[currentDeviceName] = index++
        }
      }

      return new Response(JSON.stringify({ devices }), { status: 200 })
    } catch (err: unknown) {
      console.error(`Error executing command: ${err}`)
      return new Response(JSON.stringify({ devices: [] }), { status: 200 })
    }
  }
}
