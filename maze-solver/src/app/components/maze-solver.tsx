'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';


export default function Mazesolver(){
    const [mazeText, setMazeText] = useState('');
    const [mazeImage, setMazeImage] = useState<string | null>(null);
    const [error, setError] = useState('');
    const [algorithm, setAlgorithm] = useState('bfs');
    const [loading , setLoading] = useState(false)
    const [width, setWidth] = useState(15);
    const [height, setHeight] = useState(15);
    const [useSymbols, setUseSymbols] = useState(false);
    const generateMaze = async() => {
        setLoading(true);
        setError('');
        try{
            const response = await fetch('http://localhost:5000/generate',{
                method:'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    width: Number(width),
                    height: Number(height),
                    useSymbols,
                  }),
                });
            const data = await response.json()
            setMazeText(data.mazeText)
            setMazeImage(data.image)
        }catch (error) {
            setError('Error generate img')
            console.error('Error:', error);

        }
        setLoading(false);
    };
    const solveMaze = async() => {
        if (!mazeText.trim()) {
            setError('Please enter or generate a maze first');
            return;
        }
        setLoading(true);
        setError('');
        try{
            const response = await fetch('http://localhost:5000/solve',{
                method:'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mazeText,
                    algorithm,
                  }),
                });
                const data = await response.json();
                if (!response.ok){
                    throw new Error('Fail to solve maze');
                }
                setMazeImage(data.image)
        } catch(error: any){
            setError(error.message);
            console.error('Error', error)
        }
        setLoading(false);
    };
    return(
        <Card className="w-full max-w-4xl mx-auto">
            <CardHeader>
                <CardTitle>Maze Solver</CardTitle>
            </CardHeader>
            <CardContent>
            <div className='space-y-6'>
            <div className='space-y-4'>
                <div className="flex gap-4 items-end">
                    <div className='space-y-2'>
                        <Label htmlFor='width'>Width</Label>
                        <Input
                            id ="width"
                            type="number"
                            min="5"
                            max="30"
                            value={width}
                            onChange={(e) => setWidth(Number(e.target.value))}
                            className="w-24"
                        />
                    </div>
                    <div className='space-y-2'>
                        <Label htmlFor='Height'>height</Label>
                        <Input
                            id ="height"
                            type="number"
                            min="5"
                            max="30"
                            value={height}
                            onChange={(e) => setWidth(Number(e.target.value))}
                            className="w-24"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                    <Switch
                        checked={useSymbols}
                        onCheckedChange={setUseSymbols}
                        id="symbols"
                    />
                    <Label htmlFor="symbols">Use */# format</Label>
                    </div>
                    <Button 
                        onClick={generateMaze} 
                        disabled={loading}
                    >
                        Generate Maze
                    </Button>
                </div>
            </div>


            <div className="space-y-2">
            <Label>Maze Text (Use 0/1 or */#, with S for start and E for end)</Label>
            <Textarea
              value={mazeText}
              onChange={(e) => setMazeText(e.target.value)}
              placeholder="Enter maze here or generate one..."
              className="font-mono h-48"
            />
          </div>


          <div className="flex gap-4 items-center">
            <Select
              value={algorithm}
              onValueChange={setAlgorithm}
              disabled={loading}
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Algorithm" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="bfs">BFS</SelectItem>
                <SelectItem value="dfs">DFS</SelectItem>
              </SelectContent>
            </Select>
            
            <Button 
              onClick={solveMaze} 
              disabled={!mazeText || loading}
            >
              Solve Maze
            </Button>
          </div>
          {mazeImage && (
            <div className="border rounded-lg p-4 bg-white">
              <img 
                src={`data:image/png;base64,${mazeImage}`}
                alt="Maze visualization"
                className="mx-auto"
              />
            </div>
          )}
          </div>
        </CardContent>
        </Card>
    )
}